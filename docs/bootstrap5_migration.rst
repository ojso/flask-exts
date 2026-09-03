Bootstrap 5 Migration Guide
===========================

English / 中文
----------------
This page is provided in English with a Chinese summary for easier reading.
中文说明：本页面保留英文原文，并附带中文说明，便于中英文对照阅读。


Complete guide for migrating from Bootstrap 4 + jQuery to Bootstrap 5 + Native JavaScript.

Overview
--------

This migration replaces jQuery and its dependent libraries with native JavaScript alternatives:

- **jQuery** → Removed (use native JS APIs)
- **Select2** → **Tom Select** (lightweight select component)
- **daterangepicker** → **Flatpickr** (lightweight date picker)
- **Moment.js** → **Day.js** (lightweight date library)
- **X-Editable** → **Inline Edit** (native inline editing)

Phase Completion Status
-----------------------

✅ Phase 1: Bootstrap 5 Template Migration (COMPLETED)
  - Updated data attributes: data-toggle → data-bs-toggle
  - Updated CSS utilities: mr-auto → me-auto, etc.
  - 11 template files updated

🚀 Phase 2: JavaScript Library Replacements (IN PROGRESS)
  - Tom Select for Select2
  - Flatpickr for daterangepicker
  - Day.js for Moment.js
  - Inline Edit for X-Editable

Detailed Changes
----------------

Select2 → Tom Select
~~~~~~~~~~~~~~~~~~~~

**Before (jQuery required):**

::

    <select name="category" data-toggle="select2" style="width: 100%">
        <option value="">Select...</option>
        <option value="1">Category 1</option>
        <option value="2">Category 2</option>
    </select>

    <script>
        $('[data-toggle="select2"]').select2({
            placeholder: 'Select a category...',
            allowClear: true
        });
    </script>

**After (No jQuery required):**

::

    <select name="category" data-tom-select data-placeholder="Select a category...">
        <option value="">Select...</option>
        <option value="1">Category 1</option>
        <option value="2">Category 2</option>
    </select>

    <!-- Automatically initialized by tom_select_plugin.js -->

**Programmatic Usage:**

::

    // Manual initialization
    const tomSelect = window.initTomSelect('#mySelect', {
        create: true,
        placeholder: 'Type to search...'
    });

    // Get selected value
    const value = tomSelect.getValue();

    // Set value
    tomSelect.setValue('value1');

daterangepicker → Flatpickr
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

::

    <input type="text" name="daterange" data-toggle="daterangepicker" />

    <script>
        $('[data-toggle="daterangepicker"]').daterangepicker({
            startDate: moment(),
            endDate: moment().add(7, 'days'),
            ranges: {
                'Today': [moment(), moment()],
                'Last 7 Days': [moment().subtract(6, 'days'), moment()]
            }
        });
    </script>

**After:**

::

    <!-- Single date -->
    <input type="date" data-flatpickr />

    <!-- Date range -->
    <input type="date" data-flatpickr-range />
    <input type="date" data-flatpickr-range />

    <!-- Programmatic usage -->
    <script>
        window.initFlatpickr('input[name="daterange"]', {
            mode: 'range',
            dateFormat: 'Y-m-d'
        });
    </script>

Moment.js → Day.js
~~~~~~~~~~~~~~~~~~

**Before:**

::

    <script>
        const date = moment('2024-01-15');
        const formatted = date.format('YYYY-MM-DD');
        const relative = date.fromNow();
    </script>

**After:**

::

    <script>
        const date = dayjs('2024-01-15');
        const formatted = date.format('YYYY-MM-DD');
        const relative = window.getRelativeTime('2024-01-15');
    </script>

X-Editable → Inline Edit
~~~~~~~~~~~~~~~~~~~~~~~~

**Before (jQuery + X-Editable):**

::

    <a href="#" id="username" data-type="text">John Doe</a>

    <script>
        $('#username').editable({
            url: '/api/user/username',
            title: 'Enter username'
        });
    </script>

**After (Native JS):**

::

    <span class="inline-edit"
          data-type="text"
          data-name="username"
          data-save-url="/api/user/username">
        John Doe
    </span>

    <!-- Automatically initialized by inline_edit_plugin.js -->

**Manual Initialization:**

::

    <script>
        const inlineEdit = new InlineEdit(element, {
            type: 'text',
            name: 'username',
            saveUrl: '/api/user/username',
            onSave: (data) => console.log('Saved:', data)
        });
    </script>

Migration Checklist
-------------------

Preparation
  ☐ Backup current application
  ☐ Review all jQuery usage
  ☐ Test current functionality
  ☐ Review browser support requirements

Form Elements
  ☐ Update select fields to use Tom Select
  ☐ Update date inputs to use Flatpickr
  ☐ Update datetime inputs
  ☐ Test form submission

Admin Interface
  ☐ Test admin list view
  ☐ Test admin edit forms
  ☐ Test inline editing
  ☐ Test filters and search

Templates
  ☐ Remove jQuery CDN/local script
  ☐ Add Tom Select plugin
  ☐ Add Flatpickr plugin
  ☐ Add Day.js plugin
  ☐ Add Inline Edit plugin
  ☐ Test template rendering

JavaScript
  ☐ Remove jQuery-dependent scripts
  ☐ Update event listeners to native JS
  ☐ Update AJAX calls
  ☐ Update DOM manipulation

Testing
  ☐ Manual browser testing
  ☐ Test on different browsers
  ☐ Test mobile responsiveness
  ☐ Run automated tests
  ☐ Performance testing

Browser Compatibility
---------------------

All replacement libraries support:

- Chrome/Edge 60+
- Firefox 55+
- Safari 12+
- iOS Safari 12+
- Android Browser 60+

No IE11 support (consistent with Bootstrap 5).

Performance Improvements
------------------------

Size Reduction
~~~~~~~~~~~~~~

::

    jQuery:             ~87 KB (min+gzip)
    Select2:            ~42 KB (min+gzip)
    daterangepicker:    ~8 KB (min+gzip)
    Moment.js:          ~67 KB (min+gzip)
    X-Editable:         ~25 KB (min+gzip)
    ──────────────────────────────────
    Total:              ~229 KB

Replaced by:
::

    Tom Select:         ~8 KB (min+gzip)
    Flatpickr:          ~5 KB (min+gzip)
    Day.js:             ~2 KB (min+gzip)
    Inline Edit:        ~2 KB (min+gzip)
    ──────────────────────────────────
    Total:              ~17 KB

**Savings: 92% reduction in JavaScript size**

Load Time Improvements
~~~~~~~~~~~~~~~~~~~~~~~

- Faster parsing (no jQuery abstraction layer)
- Better browser optimization
- Reduced network transfer
- Parallel loading of small libraries

Troubleshooting
---------------

Elements not initializing
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    // Ensure DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Manually initialize if needed
        window.initTomSelect('#mySelect');
    });

Tom Select styling issues
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    <!-- Ensure Bootstrap 5 CSS is loaded first -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/css/bootstrap.min.css">

    <!-- Then Tom Select CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tom-select@1.7.9/dist/css/tom-select.bootstrap5.min.css">

Flatpickr not showing calendar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    // Check console for errors
    console.log(flatpickr);

    // Manually initialize
    flatpickr('#myDate', { dateFormat: 'Y-m-d' });

Day.js timezone issues
~~~~~~~~~~~~~~~~~~~~~~

::

    // Ensure plugins are registered
    dayjs.extend(window.dayjs_plugin_utc);
    dayjs.extend(window.dayjs_plugin_timezone);

    // Use timezone-aware formatting
    const date = dayjs().tz('America/New_York').format('YYYY-MM-DD HH:mm:ss z');

Inline Edit not working
~~~~~~~~~~~~~~~~~~~~~~

::

    // Ensure element has required data attributes
    // data-type: type of input
    // data-name: field name
    // data-save-url: (optional) save endpoint

    // Check for CSRF token in page
    <meta name="csrf-token" content="...">

Migration Examples
------------------

Simple Select Field
~~~~~~~~~~~~~~~~~~~

::

    {% extends "admin/master.html" %}

    {% block content %}
    <form method="POST">
        <div class="form-group">
            <label>Status</label>
            <select name="status" data-tom-select data-placeholder="Choose status...">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
            </select>
        </div>
        <button type="submit" class="btn btn-primary">Save</button>
    </form>
    {% endblock %}

Date Range Picker
~~~~~~~~~~~~~~~~~

::

    <div class="row">
        <div class="col-md-6">
            <label>Start Date</label>
            <input type="date" name="start_date" data-flatpickr-range required>
        </div>
        <div class="col-md-6">
            <label>End Date</label>
            <input type="date" name="end_date" data-flatpickr-range required>
        </div>
    </div>

Inline Editing
~~~~~~~~~~~~~~

::

    <table class="table">
        <tr>
            <td>Username</td>
            <td>
                <span class="inline-edit"
                      data-type="text"
                      data-name="username"
                      data-save-url="/api/user/update">
                    john_doe
                </span>
            </td>
        </tr>
        <tr>
            <td>Status</td>
            <td>
                <span class="inline-edit"
                      data-type="select"
                      data-name="status"
                      data-options='{"active":"Active","inactive":"Inactive"}'
                      data-save-url="/api/user/update">
                    active
                </span>
            </td>
        </tr>
    </table>

Rollback Plan
-------------

If issues arise:

1. Keep old bootstrap4 branch
2. Test thoroughly before deploying
3. Monitor application logs
4. Have quick rollback plan ready
5. Communicate changes to users

Support and Resources
---------------------

- `Tom Select Documentation <https://tom-select.js.org/>`_
- `Flatpickr Documentation <https://flatpickr.js.org/>`_
- `Day.js Documentation <https://day.js.org/>`_
- `Bootstrap 5 Guide <https://getbootstrap.com/docs/5.0/>`_
- Flask-Exts Documentation

See Also
--------

- :doc:`performance` - Performance optimization
- :doc:`theming` - Theme customization
- :doc:`extension_development` - Building extensions
