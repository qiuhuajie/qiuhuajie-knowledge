const { Plugin, requestUrl } = require("obsidian");

const CACHE_VERSION = 1;

module.exports = class ExternalLinkCardsPlugin extends Plugin {
  async onload() {
    const data = await this.loadData();
    this.cache = data?.version === CACHE_VERSION ? data.cache || {} : {};
    this.inFlight = new Map();

    this.registerMarkdownPostProcessor((element) => {
      this.renderLinkCards(element);
    });
  }

  renderLinkCards(root) {
    const candidates = Array.from(root.querySelectorAll("p, li"));

    for (const container of candidates) {
      if (container.dataset.externalLinkCardProcessed === "true") {
        continue;
      }

      const anchor = this.getStandaloneExternalAnchor(container);
      if (!anchor) {
        continue;
      }

      container.dataset.externalLinkCardProcessed = "true";
      container.classList.add("external-link-card-container");

      const url = anchor.href;
      const card = this.createCard(url, anchor.textContent.trim());
      container.empty();
      container.appendChild(card);

      this.populateCard(card, url);
    }
  }

  getStandaloneExternalAnchor(container) {
    const clone = container.cloneNode(true);
    clone.querySelectorAll("ul, ol").forEach((node) => node.remove());

    const anchors = Array.from(clone.querySelectorAll("a[href]")).filter((anchor) =>
      this.isExternalUrl(anchor.href)
    );

    if (anchors.length !== 1) {
      return null;
    }

    const cloneText = clone.textContent.trim();
    const anchorText = anchors[0].textContent.trim();
    if (cloneText !== anchorText) {
      return null;
    }

    return Array.from(container.querySelectorAll("a[href]")).find((anchor) =>
      this.isExternalUrl(anchor.href)
    );
  }

  isExternalUrl(url) {
    return /^https?:\/\//i.test(url);
  }

  createCard(url, fallbackTitle) {
    const parsed = this.parseUrl(url);
    const hostname = parsed?.hostname || url;

    const card = document.createElement("a");
    card.className = "external-link-card";
    card.href = url;
    card.dataset.url = url;

    const favicon = document.createElement("img");
    favicon.className = "external-link-card-favicon";
    favicon.alt = "";
    favicon.src = `https://icons.duckduckgo.com/ip3/${hostname}.ico`;

    const body = document.createElement("span");
    body.className = "external-link-card-body";

    const title = document.createElement("span");
    title.className = "external-link-card-title";
    title.textContent = this.cleanTitle(fallbackTitle || hostname);

    const description = document.createElement("span");
    description.className = "external-link-card-description";
    description.textContent = url;

    const site = document.createElement("span");
    site.className = "external-link-card-site";
    site.textContent = hostname;

    body.append(title, description, site);
    card.append(favicon, body);

    return card;
  }

  async populateCard(card, url) {
    const cached = this.cache[url];
    if (cached) {
      this.updateCard(card, cached);
      return;
    }

    const metadata = await this.fetchMetadata(url);
    if (metadata) {
      this.updateCard(card, metadata);
    }
  }

  updateCard(card, metadata) {
    const title = card.querySelector(".external-link-card-title");
    const description = card.querySelector(".external-link-card-description");
    const site = card.querySelector(".external-link-card-site");
    const favicon = card.querySelector(".external-link-card-favicon");

    if (title && metadata.title) {
      title.textContent = metadata.title;
    }

    if (description) {
      description.textContent = metadata.description || metadata.url;
    }

    if (site) {
      site.textContent = metadata.siteName || metadata.hostname;
    }

    if (favicon && metadata.favicon) {
      favicon.src = metadata.favicon;
    }

    if (metadata.image && !card.querySelector(".external-link-card-image")) {
      const image = document.createElement("img");
      image.className = "external-link-card-image";
      image.alt = "";
      image.src = metadata.image;
      card.appendChild(image);
    }
  }

  async fetchMetadata(url) {
    if (this.inFlight.has(url)) {
      return this.inFlight.get(url);
    }

    const promise = this.doFetchMetadata(url).finally(() => {
      this.inFlight.delete(url);
    });

    this.inFlight.set(url, promise);
    return promise;
  }

  async doFetchMetadata(url) {
    const parsed = this.parseUrl(url);
    if (!parsed) {
      return null;
    }

    try {
      const response = await requestUrl({ url });
      const html = response.text;
      const doc = new DOMParser().parseFromString(html, "text/html");

      const metadata = {
        url,
        hostname: parsed.hostname,
        title: this.cleanTitle(
          this.getMeta(doc, "og:title") ||
            this.getMeta(doc, "twitter:title") ||
            doc.querySelector("title")?.textContent ||
            parsed.hostname
        ),
        description: this.cleanText(
          this.getMeta(doc, "og:description") ||
            this.getMeta(doc, "description") ||
            this.getMeta(doc, "twitter:description") ||
            url
        ),
        siteName: this.cleanText(this.getMeta(doc, "og:site_name") || parsed.hostname),
        image: this.resolveUrl(
          this.getMeta(doc, "og:image") || this.getMeta(doc, "twitter:image"),
          parsed
        ),
        favicon: `https://icons.duckduckgo.com/ip3/${parsed.hostname}.ico`,
      };

      if (this.isBlockedTitle(metadata.title)) {
        metadata.title = url;
        metadata.description = url;
        metadata.siteName = parsed.hostname;
      }

      this.cache[url] = metadata;
      await this.saveData({ version: CACHE_VERSION, cache: this.cache });
      return metadata;
    } catch (error) {
      console.warn("[External Link Cards] Failed to fetch metadata:", url, error);
      return null;
    }
  }

  getMeta(doc, name) {
    return (
      doc.querySelector(`meta[property="${name}"]`)?.getAttribute("content") ||
      doc.querySelector(`meta[name="${name}"]`)?.getAttribute("content") ||
      ""
    );
  }

  resolveUrl(value, baseUrl) {
    if (!value) {
      return "";
    }

    try {
      return new URL(value, baseUrl).href;
    } catch {
      return "";
    }
  }

  parseUrl(url) {
    try {
      return new URL(url);
    } catch {
      return null;
    }
  }

  cleanTitle(value) {
    return this.cleanText(value).replace(/\s*[-|]\s*$/, "");
  }

  isBlockedTitle(value) {
    return /域名拦截|访问拦截|安全验证|blocked|access denied/i.test(value || "");
  }

  cleanText(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }
};
