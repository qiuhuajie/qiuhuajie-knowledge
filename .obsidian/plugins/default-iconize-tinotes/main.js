const { Plugin, Notice, TFile, TFolder } = require("obsidian");

const ICONIZE_PLUGIN_ID = "obsidian-icon-folder";
const ICONIZE_DATA_PATH = ".obsidian/plugins/obsidian-icon-folder/data.json";
const DEFAULT_ICON = "TiNotes";
const CREATE_RETRY_DELAYS = [500, 1500, 4000];

module.exports = class DefaultIconizeTiNotesPlugin extends Plugin {
  async onload() {
    this.writeQueue = Promise.resolve();

    this.app.workspace.onLayoutReady(() => {
      this.queueBackfillMissingIcons();
    });

    this.registerEvent(
      this.app.vault.on("create", (item) => {
        this.applyDefaultIcon(item);
      })
    );

    this.addCommand({
      id: "backfill-missing-tinotes-icons",
      name: "Backfill missing TiNotes icons for notes and folders",
      callback: () => this.backfillMissingIcons({ showNotice: true }),
    });
  }

  shouldHandle(item) {
    if (!item || !item.path || item.path.startsWith(".")) {
      return false;
    }

    if (item instanceof TFolder) {
      return item.path.length > 0;
    }

    return item instanceof TFile && item.extension === "md";
  }

  async applyDefaultIcon(item) {
    if (!this.shouldHandle(item)) {
      return;
    }

    for (const delay of CREATE_RETRY_DELAYS) {
      this.registerTimeout(
        window.setTimeout(() => {
          this.queueSetIconIfMissing(item.path);
          this.queueBackfillMissingIcons();
        }, delay)
      );
    }

    return this.writeQueue;
  }

  queueSetIconIfMissing(path) {
    this.writeQueue = this.writeQueue
      .then(() => this.setIconIfMissing(path))
      .catch((error) => {
        console.error("[Default Iconize TiNotes] Failed to set icon", error);
      });

    return this.writeQueue;
  }

  async setIconIfMissing(path) {
    const iconize = this.app.plugins.plugins[ICONIZE_PLUGIN_ID];
    if (iconize && typeof iconize.getIconNameFromPath === "function") {
      const currentIcon = iconize.getIconNameFromPath(path);
      if (currentIcon) {
        return false;
      }

      if (typeof iconize.addFolderIcon === "function") {
        iconize.addFolderIcon(path, DEFAULT_ICON);
        this.refreshIconInFileExplorer(path);
        return true;
      }
    }

    return this.writeIconizeDataIfMissing(path);
  }

  async writeIconizeDataIfMissing(path) {
    const exists = await this.app.vault.adapter.exists(ICONIZE_DATA_PATH);
    if (!exists) {
      return false;
    }

    const raw = await this.app.vault.adapter.read(ICONIZE_DATA_PATH);
    const data = JSON.parse(raw);
    if (data[path]) {
      return false;
    }

    data[path] = DEFAULT_ICON;
    await this.app.vault.adapter.write(
      ICONIZE_DATA_PATH,
      `${JSON.stringify(data, null, 2)}\n`
    );
    this.refreshIconInFileExplorer(path);
    return true;
  }

  queueBackfillMissingIcons() {
    this.writeQueue = this.writeQueue
      .then(() => this.backfillMissingIcons({ showNotice: false }))
      .catch((error) => {
        console.error("[Default Iconize TiNotes] Failed to backfill icons", error);
      });

    return this.writeQueue;
  }

  async backfillMissingIcons({ showNotice } = { showNotice: false }) {
    let count = 0;
    const items = [
      ...this.app.vault.getMarkdownFiles(),
      ...this.getAllFolders(this.app.vault.getRoot()),
    ];

    for (const item of items) {
      if (this.shouldHandle(item)) {
        const changed = await this.setIconIfMissing(item.path);
        if (changed) {
          count += 1;
        }
      }
    }

    if (showNotice) {
      new Notice(`Default Iconize TiNotes: added ${count} missing icon(s).`);
    }
  }

  getAllFolders(folder) {
    const folders = [];
    for (const child of folder.children) {
      if (child instanceof TFolder) {
        folders.push(child, ...this.getAllFolders(child));
      }
    }
    return folders;
  }

  refreshIconInFileExplorer(path) {
    const iconize = this.app.plugins.plugins[ICONIZE_PLUGIN_ID];
    const node = Array.from(document.querySelectorAll("[data-path]")).find(
      (element) => element.getAttribute("data-path") === path
    );

    if (node && iconize?.api?.setIconForNode) {
      const titleNode =
        node.querySelector(".nav-folder-title-content") ||
        node.querySelector(".nav-file-title-content");

      if (titleNode) {
        let iconNode = node.querySelector(".iconize-icon");
        if (!iconNode) {
          iconNode = document.createElement("div");
          iconNode.classList.add("iconize-icon");
          node.insertBefore(iconNode, titleNode);
        }

        iconNode.setAttribute("data-icon", DEFAULT_ICON);
        iconize.api.setIconForNode(DEFAULT_ICON, iconNode);
      }
    }

    if (typeof iconize?.handleChangeLayout === "function") {
      iconize.handleChangeLayout();
    }

    this.app.workspace.trigger("layout-change");
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
};
