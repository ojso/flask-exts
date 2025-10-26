function detail_filter() {
  const faFilter = document.getElementById('detail_filter');
  if (faFilter) {
    function filterTable(searchValue) {
      const rex = new RegExp(searchValue, 'i');
      const searchableRows = document.querySelectorAll('.searchable tr');
      searchableRows.forEach(function (row) {
        const rowText = row.textContent || row.innerText;
        if (rex.test(rowText)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      })
    }
    let debounceTimer;
    faFilter.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        filterTable(this.value);
      }, 500); // 500ms delay
    });
  }
}

