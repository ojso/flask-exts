class SearchDetail {
  constructor(searchId) {
    this.searchInput = document.getElementById(searchId);
    this.timeoutId = null;
    this.delay = 500; // 500ms delay
    this.lastValue = '';
    this.searchableRows = null; // no query at constructor
    if (this.searchInput) {
      this.searchInput.addEventListener('input', this.handleInput);
    }
  }

  handleInput = (event) => {
    const value = event.target.value.trim();
    if (value === this.lastValue) {
      return;
    }
    this.clearTimeout();
    this.timeoutId = setTimeout(() => {
      this.lastValue = value;
      this.performSearch(value);
    }, this.delay);
  }

  clearTimeout() {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
  }

  performSearch(value) {
    let rex;
    try {
      rex = new RegExp(value, 'i');
    } catch (e) {
      // If the input is not a valid regex, fall back to literal matching.
      const escaped = value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      rex = new RegExp(escaped, 'i');
    }

    if (this.searchableRows == null) {
      this.searchableRows = document.querySelectorAll('.searchable tr');
    }
    this.searchableRows.forEach(function (row) {
      const rowText = row.textContent || '';
      row.style.display = rex.test(rowText) ? '' : 'none';
    });
  }

  destroy() {
    this.clearTimeout();
    if (this.searchInput) {
      this.searchInput.removeEventListener('input', this.handleInput);
    }
  }

}

