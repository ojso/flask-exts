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
    const rex = new RegExp(value, 'i');
    if (this.searchableRows == null) {
      this.searchableRows = document.querySelectorAll('.searchable tr');
    }
    this.searchableRows.forEach(function (row) {
      const rowText = row.textContent;
      if (rex.test(rowText)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    })
  }

  destroy() {
    this.clearTimeout();
    if (this.searchInput) {
      this.searchInput.removeEventListener('input', this.handleInput);
    }
  }
  
}

