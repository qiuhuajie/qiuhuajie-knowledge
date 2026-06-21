const { Plugin } = require("obsidian");

module.exports = class CollapseDescendantFoldersPlugin extends Plugin {
  async onload() {
    this.observers = [];
    this.pendingPaths = new Set();
    this.flushTimer = null;

    this.app.workspace.onLayoutReady(() => {
      this.registerFileExplorerObservers();
    });

    this.registerEvent(
      this.app.workspace.on("layout-change", () => {
        this.registerFileExplorerObservers();
      })
    );
  }

  onunload() {
    for (const observer of this.observers) {
      observer.disconnect();
    }
    this.observers = [];

    if (this.flushTimer !== null) {
      window.clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
  }

  registerFileExplorerObservers() {
    for (const observer of this.observers) {
      observer.disconnect();
    }
    this.observers = [];

    for (const leaf of this.app.workspace.getLeavesOfType("file-explorer")) {
      const container = leaf.view?.navFileContainerEl?.parentElement;
      if (!container) {
        continue;
      }

      const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
          if (mutation.type !== "attributes" || mutation.attributeName !== "class") {
            continue;
          }

          const folderEl = mutation.target;
          if (!folderEl.classList?.contains("nav-folder")) {
            continue;
          }

          if (!folderEl.classList.contains("is-collapsed")) {
            continue;
          }

          const path = folderEl
            .querySelector(":scope > .nav-folder-title")
            ?.getAttribute("data-path");

          if (path) {
            this.queueCollapseDescendants(path);
          }
        }
      });

      observer.observe(container, {
        subtree: true,
        attributes: true,
        attributeFilter: ["class"],
      });

      this.observers.push(observer);
    }
  }

  queueCollapseDescendants(path) {
    this.pendingPaths.add(path);

    if (this.flushTimer !== null) {
      return;
    }

    this.flushTimer = window.setTimeout(() => {
      const paths = Array.from(this.pendingPaths);
      this.pendingPaths.clear();
      this.flushTimer = null;

      for (const path of paths) {
        this.collapseDescendants(path);
      }
    }, 0);
  }

  collapseDescendants(parentPath) {
    const prefix = `${parentPath}/`;

    for (const leaf of this.app.workspace.getLeavesOfType("file-explorer")) {
      const fileItems = leaf.view?.fileItems || {};

      for (const [path, item] of Object.entries(fileItems)) {
        if (!path.startsWith(prefix)) {
          continue;
        }

        if (typeof item?.setCollapsed === "function") {
          item.setCollapsed(true);
        }
      }
    }
  }
};
