var AdminFilters = function (element, filtersElement, filterGroups, activeFilters) {
    var root = document.querySelector(element);
    if (!root) return;
    var container = root.querySelector('.filters');
    if (!container) return;
    var lastCount = 0;

    function getCount(name) {
        var idx = name.indexOf('_');

        if (idx === -1) {
            return 0;
        }

        return parseInt(name.substr(3, idx - 3), 10);
    }

    function makeName(name) {
        var result = 'flt' + lastCount + '_' + name;
        lastCount += 1;
        return result;
    }

    function buttons() {
        return Array.prototype.slice.call(root.querySelectorAll('button'));
    }

    function btnLinks() {
        return Array.prototype.slice.call(root.querySelectorAll('a.btn'));
    }

    function showButtons() {
        buttons().forEach(function (el) {
            el.classList.remove('d-none');
        });
        btnLinks().forEach(function (el) {
            el.classList.remove('d-none');
        });
    }

    function hideButtons() {
        buttons().forEach(function (el) {
            el.classList.add('d-none');
        });
        btnLinks().forEach(function (el) {
            el.classList.add('d-none');
        });
    }

    function removeFilter() {
        var tr = this.closest('tr');
        if (tr) tr.remove();
        if (container.querySelectorAll('tr').length == 0) {
            hideButtons();
            var tbody = container.querySelector('tbody');
            if (tbody) tbody.remove();
        } else {
            showButtons();
        }

        return false;
    }

    // triggered when the filter operation (equals, not equals, etc) is changed
    function changeOperation(subfilters, tr, filter, select) {
        // get the filter_group subfilter based on the value of the selected option
        var arg = select.tomselect ? select.tomselect.getValue() : select.value;
        var selectedFilter = subfilters.find(function (el) {
            return el.index == arg;
        });
        var tds = tr.querySelectorAll('td');
        var inputContainer = tds[tds.length - 1];

        // recreate and style the input field (turn into date range or tom-select if necessary)
        var field = createFilterInput(inputContainer, null, selectedFilter);
        styleFilterInput(selectedFilter, field);

        showButtons();
    }

    // generate HTML for filter input - allows changing filter input type to one with options or tags
    function createFilterInput(inputContainer, filterValue, filter) {
        var field;
        if (filter.type == "text") {
            field = document.createElement('input');
            field.type = 'text';
            field.className = 'filter-val form-control';
            field.name = makeName(filter.arg);
            field.value = filterValue || '';
        } else if (filter.options) {
            field = document.createElement('select');
            field.className = 'filter-val';
            field.name = makeName(filter.arg);

            filter.options.forEach(function (option) {
                var opt = document.createElement('option');
                opt.value = option[0];
                opt.textContent = option[1];
                // for active filter inputs with options, add "selected" if there is a matching active filter
                if (filterValue && (filterValue == option[0])) {
                    opt.selected = true;
                }
                field.appendChild(opt);
            });
        } else {
            field = document.createElement('input');
            field.type = 'text';
            field.className = 'filter-val form-control';
            field.name = makeName(filter.arg);
            field.value = filterValue || '';
        }

        var td = document.createElement('td');
        td.appendChild(field);
        inputContainer.replaceWith(td);

        // show "Apply Filter" button when filter input is changed
        field.addEventListener('input', function () {
            showButtons();
        });
        field.addEventListener('change', function () {
            showButtons();
        });

        return field;
    }

    // add styling to input field, accommodates filters that change the input field's HTML
    function styleFilterInput(filter, field) {
        if (filter.type) {
            if ((filter.type == "datepicker") || (filter.type == "daterangepicker")) {
                field.setAttribute('data-date-format', "YYYY-MM-DD");
            } else if ((filter.type == "datetimepicker") || (filter.type == "datetimerangepicker")) {
                field.setAttribute('data-date-format', "YYYY-MM-DD HH:mm:ss");
            } else if ((filter.type == "timepicker") || (filter.type == "timerangepicker")) {
                field.setAttribute('data-date-format', "HH:mm:ss");
            }
            if (window.faForm) {
                window.faForm.applyStyle(field, filter.type);
            }
        } else if (filter.options) {
            filter.type = "select";
            if (window.faForm) {
                window.faForm.applyStyle(field, filter.type);
            }
        }

        return field;
    }

    function addFilter(name, subfilters, selectedIndex, filterValue) {
        var tr = document.createElement('tr');
        tr.className = 'form-horizontal';
        container.appendChild(tr);

        // Filter list
        var td1 = document.createElement('td');
        var removeA = document.createElement('a');
        removeA.href = '#';
        removeA.className = 'btn btn-default remove-filter';
        removeA.addEventListener('click', removeFilter);
        var closeSpan = document.createElement('span');
        closeSpan.className = 'close-icon';
        closeSpan.textContent = '\u00d7';
        removeA.appendChild(closeSpan);
        removeA.appendChild(document.createTextNode('\u00a0' + name));
        td1.appendChild(removeA);
        tr.appendChild(td1);

        // Filter operation <select> (equal, not equal, etc)
        var select = document.createElement('select');
        select.className = 'filter-op';

        // if one of the subfilters are selected, use that subfilter to create the input field
        var filterSelection = 0;
        subfilters.forEach(function (subfilter, subfilterIndex) {
            var opt = document.createElement('option');
            opt.value = subfilter.arg;
            opt.textContent = subfilter.operation;
            if (subfilter.index == selectedIndex) {
                opt.selected = true;
                filterSelection = subfilterIndex;
            } else {
                opt.selected = false;
            }
            select.appendChild(opt);
        });

        var td2 = document.createElement('td');
        td2.appendChild(select);
        tr.appendChild(td2);

        // get filter option from filter_group, only for new filter creation
        var filter = subfilters[filterSelection];

        select.addEventListener('change', function () {
            changeOperation(subfilters, tr, filter, select);
        });

        var inputContainer = document.createElement('td');
        tr.appendChild(inputContainer);

        var newFilterField = createFilterInput(inputContainer, filterValue, filter);
        newFilterField.focus();
        var styledFilterField = styleFilterInput(filter, newFilterField);

        return styledFilterField;
    }

    // Add Filter Button, new filter
    var filtersMenu = document.querySelector(filtersElement);
    if (filtersMenu) {
        filtersMenu.querySelectorAll('a.filter').forEach(function (el) {
            el.addEventListener('click', function () {
                var name = el.textContent.trim();
                addFilter(name, filterGroups[name], false, null);
                showButtons();
            });
        });
    }

    // on page load - add active filters
    activeFilters.forEach(function (activeFilter) {
        var idx = activeFilter[0],
            name = activeFilter[1],
            filterValue = activeFilter[2];
        addFilter(name, filterGroups[name], idx, filterValue);
    });

    // show "Apply Filter" button when filter input is changed
    root.querySelectorAll('.filter-val').forEach(function (el) {
        el.addEventListener('input', function () {
            showButtons();
        });
        el.addEventListener('change', function () {
            showButtons();
        });
    });

    root.querySelectorAll('.remove-filter').forEach(function (el) {
        el.addEventListener('click', removeFilter);
    });

    root.querySelectorAll('.filter-val:not(.filter-op)').forEach(function (el) {
        var count = getCount(el.getAttribute('name'));
        if (count > lastCount)
            lastCount = count;
    });

    lastCount += 1;
};


document.addEventListener('DOMContentLoaded', function () {
    var dataEl = document.getElementById('filter-groups-data');
    if (dataEl) {
        var filtersEl = document.getElementById('active-filters-data');
        new AdminFilters(
            '#filter_form', '.field-filters',
            JSON.parse(dataEl.textContent),
            filtersEl ? JSON.parse(filtersEl.textContent) : []
        );
    }
});