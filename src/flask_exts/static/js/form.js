(function () {
  var AdminForm = function () {
    // Field converters
    var fieldConverters = [];

    // convert moment-style date format to flatpickr format tokens
    function toFlatpickrFormat(fmt) {
      if (!fmt) return fmt;
      return fmt
        .replace(/YYYY/g, 'Y')
        .replace(/MM/g, 'm')
        .replace(/DD/g, 'd')
        .replace(/HH/g, 'H')
        .replace(/mm/g, 'i')
        .replace(/ss/g, 'S');
    }

    function hasSeconds(fmt) {
      return !!fmt && fmt.indexOf('ss') !== -1;
    }

    function notifyFilterChange() {
      document.querySelectorAll('.filter-val').forEach(function (el) {
        el.dispatchEvent(new Event('change', { bubbles: true }));
      });
    }

    /**
    * Process AJAX fk-widget (Tom Select with remote data)
    */
    function processAjaxWidget(el, name, parent) {
      if (!window.TomSelect) {
        console.error('Tom Select is required for tom-select-ajax fields');
        return false;
      }
      var multiple = el.getAttribute('data-multiple') == '1';
      var minimumInputLength = parseInt(el.getAttribute('data-minimum-input-length'), 10) || 1;
      var placeholder = el.getAttribute('data-placeholder');
      var separator = el.getAttribute('data-separator') || ',';
      var allowBlank = el.getAttribute('data-allow-blank') === '1';
      var url = el.getAttribute('data-url');
      var initialJson = el.getAttribute('data-json');

      if (allowBlank && !multiple) {
        var blankOpt = document.createElement('option');
        blankOpt.value = '';
        blankOpt.textContent = '';
        el.appendChild(blankOpt);
      }

      // pre-populate initial (already selected) values
      if (initialJson) {
        var value = JSON.parse(initialJson);
        if (value) {
          if (multiple) {
            value.forEach(function (v) {
              var opt = document.createElement('option');
              opt.value = String(v[0]);
              opt.textContent = v[1];
              opt.selected = true;
              el.appendChild(opt);
            });
          } else {
            var first = value[0] !== undefined ? value[0] : (Array.isArray(value) ? value[0] : value);
            var text = value[1] !== undefined ? value[1] : value;
            var opt2 = document.createElement('option');
            opt2.value = String(first);
            opt2.textContent = text;
            opt2.selected = true;
            el.appendChild(opt2);
          }
        }
      }

      function loadAjaxOptions(query, offset) {
        var sep = url.indexOf('?') > -1 ? '&' : '?';
        return fetch(
          url + sep + 'query=' + encodeURIComponent(query) + '&offset=' + offset + '&limit=10'
        )
          .then(function (res) { return res.json(); })
          .then(function (data) {
            var results = [];
            for (var k in data) {
              var v = data[k];
              results.push({ id: String(v[0]), text: v[1] });
            }
            return results;
          });
      }

      var page = 0;

      var opts = {
        valueField: 'id',
        labelField: 'text',
        searchField: 'text',
        maxItems: multiple ? null : 1,
        placeholder: placeholder || undefined,
        allowEmptyOption: allowBlank,
        create: false,
        shouldLoad: function (query) {
          return query.length >= minimumInputLength;
        },
        load: function (query, callback) {
          page = 0;
          loadAjaxOptions(query, 0)
            .then(function (results) {
              callback(results);
            })
            .catch(function () {
              callback();
            });
        },
        onDropdownOpen: function () {
          // load first page when dropdown opens with an empty query
          if (this.lastQuery && this.lastQuery.length >= minimumInputLength) return;
        }
      };

      if (parent) opts.dropdownParent = parent;

      new TomSelect(el, opts);
      return true;
    }

    /**
     * Process Leaflet (map) widget
     */
    function processLeafletWidget(el, name) {
      if (!window.L) {
        console.error('Leaflet library is not loaded. Add the leaflet plugin to use the map widget.');
        return false;
      }
      if (!window.FLASK_EXTS_MAPS) {
        console.error("You must set FLASK_EXTS_MAPS in your Flask settings to use the map widget");
        return false;
      }
      if (!window.FLASK_EXTS_DEFAULT_CENTER_LAT || !window.FLASK_EXTS_DEFAULT_CENTER_LONG) {
        console.error("You must set FLASK_EXTS_DEFAULT_CENTER_LAT and FLASK_EXTS_DEFAULT_CENTER_LONG in your Flask settings to use the map widget");
        return false;
      }

      var geometryType = el.getAttribute('data-geometry-type');
      if (geometryType) {
        geometryType = geometryType.toUpperCase();
      } else {
        geometryType = 'GEOMETRY';
      }
      var multiple = geometryType.lastIndexOf('MULTI', geometryType) === 0;
      var editable = !el.disabled;

      var mapDiv = document.createElement('div');
      mapDiv.style.width = el.getAttribute('data-width') + 'px';
      mapDiv.style.height = el.getAttribute('data-height') + 'px';
      el.insertAdjacentElement('afterend', mapDiv);
      el.style.display = 'none';

      var center = null;
      if (el.getAttribute('data-lat') && el.getAttribute('data-lng')) {
        center = L.latLng(el.getAttribute('data-lat'), el.getAttribute('data-lng'));
      }

      var maxBounds = null;
      if (
        el.getAttribute('data-max-bounds-sw-lat') && el.getAttribute('data-max-bounds-sw-lng') &&
        el.getAttribute('data-max-bounds-ne-lat') && el.getAttribute('data-max-bounds-ne-lng')
      ) {
        maxBounds = L.latLngBounds(
          L.latLng(el.getAttribute('data-max-bounds-sw-lat'), el.getAttribute('data-max-bounds-sw-lng')),
          L.latLng(el.getAttribute('data-max-bounds-ne-lat'), el.getAttribute('data-max-bounds-ne-lng'))
        );
      }

      var editableLayers;
      if (el.value) {
        editableLayers = new L.geoJson(JSON.parse(el.value));
        center = center || editableLayers.getBounds().getCenter();
      } else {
        editableLayers = new L.geoJson();
      }

      var mapOptions = {
        center: center,
        zoom: parseInt(el.getAttribute('data-zoom'), 10) || 12,
        minZoom: parseInt(el.getAttribute('data-min-zoom'), 10) || undefined,
        maxZoom: parseInt(el.getAttribute('data-max-zoom'), 10) || undefined,
        maxBounds: maxBounds
      };

      if (!editable) {
        mapOptions.dragging = false;
        mapOptions.touchzoom = false;
        mapOptions.scrollWheelZoom = false;
        mapOptions.doubleClickZoom = false;
        mapOptions.boxZoom = false;
        mapOptions.tap = false;
        mapOptions.keyboard = false;
        mapOptions.zoomControl = false;
      }

      // only show attributions if the map is big enough
      // (otherwise, it gets in the way)
      var mapW = parseInt(el.getAttribute('data-width'), 10) || 0;
      var mapH = parseInt(el.getAttribute('data-height'), 10) || 0;
      if (mapW * mapH < 10000) {
        mapOptions.attributionControl = false;
      }

      var map = L.map(mapDiv, mapOptions);
      map.addLayer(editableLayers);

      if (center) {
        // if we have more than one point, make the map show everything
        var bounds = editableLayers.getBounds();
        if (!bounds.getNorthEast().equals(bounds.getSouthWest())) {
          map.fitBounds(bounds);
        }
      } else {
        // use the default map center
        map.setView([window.FLASK_EXTS_DEFAULT_CENTER_LAT, window.FLASK_EXTS_DEFAULT_CENTER_LONG], 12);
      }

      // set up tiles
      var mapboxHostnameAndPath = el.getAttribute('data-tile-layer-url') || 'api.mapbox.com/styles/v1/mapbox/' + window.FLASK_EXTS_MAPBOX_MAP_ID + '/tiles/{z}/{x}/{y}?access_token={accessToken}';
      var attribution = el.getAttribute('data-tile-layer-attribution') || 'Map data &copy; <a href="//openstreetmap.org">OpenStreetMap</a> contributors, <a href="//creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="//mapbox.com">Mapbox</a>';
      L.tileLayer('//' + mapboxHostnameAndPath, {
        // Attributes from https://docs.mapbox.com/help/troubleshooting/migrate-legacy-static-tiles-api/
        attribution: attribution,
        maxZoom: 18,
        tileSize: 512,
        zoomOffset: -1,
        accessToken: window.FLASK_EXTS_MAPBOX_ACCESS_TOKEN
      }).addTo(map);

      // everything below here is to set up editing, so if we're not editable,
      // we can just return early.
      if (!editable) {
        return true;
      }

      // set up Leaflet.draw editor
      var drawOptions = {
        draw: {
          // circles are not geometries in geojson
          circle: false,
          circlemarker: false
        },
        edit: {
          featureGroup: editableLayers
        }
      };

      if (['POINT', 'MULTIPOINT'].indexOf(geometryType) > -1) {
        drawOptions.draw.polyline = false;
        drawOptions.draw.polygon = false;
        drawOptions.draw.rectangle = false;
      } else if (['LINESTRING', 'MULTILINESTRING'].indexOf(geometryType) > -1) {
        drawOptions.draw.marker = false;
        drawOptions.draw.polygon = false;
        drawOptions.draw.rectangle = false;
      } else if (['POLYGON', 'MULTIPOLYGON'].indexOf(geometryType) > -1) {
        drawOptions.draw.marker = false;
        drawOptions.draw.polyline = false;
      }
      var drawControl = new L.Control.Draw(drawOptions);
      map.addControl(drawControl);
      if (window.FLASK_EXTS_MAPS_SEARCH) {
        var circle = L.circleMarker([0, 0]);
        var autocompleteEl = document.createElement('input');
        autocompleteEl.style.position = 'absolute';
        autocompleteEl.style.zIndex = '9999';
        autocompleteEl.style.display = 'block';
        autocompleteEl.style.margin = '-42px 0 0 10px';
        autocompleteEl.style.width = '50%';
        var form = el.form;

        mapDiv.insertAdjacentElement('afterend', autocompleteEl);
        form.addEventListener('submit', function (evt) {
          if (document.activeElement === autocompleteEl) {
            evt.preventDefault();
            return false;
          }
        });
        var autocomplete = new google.maps.places.Autocomplete(autocompleteEl);
        autocomplete.addListener('place_changed', function () {
          var place = autocomplete.getPlace();
          var loc = place.geometry.location;
          var viewport = place.geometry.viewport;
          circle.setLatLng(L.latLng(loc.lat(), loc.lng()));
          circle.addTo(map);
          if (viewport) {
            map.fitBounds([
              viewport.getNorthEast().toJSON(),
              viewport.getSouthWest().toJSON(),
            ]);
          }
          else {
            map.fitBounds(circle.getBounds());
          }
        });
      }

      // save when the editableLayers are edited
      var saveToTextArea = function () {
        var geo = editableLayers.toGeoJSON();
        if (geo.features.length === 0) {
          el.value = '';
          return true;
        }
        if (multiple) {
          var coords = geo.features.map(function (feature) {
            return [feature.geometry.coordinates];
          });
          geo = {
            'type': geometryType,
            'coordinates': coords
          };
        } else {
          geo = geo.features[0].geometry;
        }
        el.value = JSON.stringify(geo);
      };

      // handle creation
      map.on('draw:created', function (e) {
        if (!multiple) {
          editableLayers.clearLayers();
        }
        editableLayers.addLayer(e.layer);
        saveToTextArea();
      });
      map.on('draw:edited', saveToTextArea);
      map.on('draw:deleted', saveToTextArea);    
    }

    /**
    * Process data-role attribute for the given input element. Feel free to override
    *
    * @param {Element} el DOM element
    * @param {String} name data-role value
    * @param {Element} parent 
    */
    this.applyStyle = function (el, name, parent) {
      // Process converters first
      for (var conv in fieldConverters) {
        var fieldConv = fieldConverters[conv];

        if (fieldConv(el, name))
          return true;
      }

      if (el.dataset && el.dataset.faInitialized) return true;

      // guard for non-browser environments / unsupported roles
      if (!(el instanceof Element)) return false;

      switch (name) {
        case 'tom-select':
          if (!window.TomSelect) return true;
          var opts2 = {
            valueField: 'value',
            labelField: 'text',
            searchField: 'text',
            maxItems: el.multiple ? null : 1,
            placeholder: el.getAttribute('data-placeholder') || undefined,
            allowEmptyOption: el.getAttribute('data-allow-blank') !== null || el.getAttribute('data-allow-blank') === '1'
          };

          if (el.getAttribute('data-tags')) {
            opts2.create = true;
            opts2.delimiter = ',';
            try {
              opts2.options = JSON.parse(el.getAttribute('data-tags'));
            } catch (e) { /* ignore malformed tags */ }
          }

          if (opts2.allowEmptyOption) {
            var hasEmpty = false;
            el.querySelectorAll('option').forEach(function (o) {
              if (o.value === '') hasEmpty = true;
            });
            if (!hasEmpty) {
              var emptyOpt = document.createElement('option');
              emptyOpt.value = '';
              emptyOpt.textContent = '';
              el.insertBefore(emptyOpt, el.firstChild);
            }
          }

          if (parent) opts2.dropdownParent = parent;
          new TomSelect(el, opts2);
          el.dataset.faInitialized = '1';
          return true;
        case 'tom-select-ajax':
          processAjaxWidget(el, name, parent);
          el.dataset.faInitialized = '1';
          return true;
        case 'datetimepicker':
          if (!window.flatpickr) return true;
          flatpickr(el, {
            enableTime: true,
            time_24hr: true,
            enableSeconds: hasSeconds(el.getAttribute('data-date-format')),
            minuteIncrement: 1,
            dateFormat: toFlatpickrFormat(el.getAttribute('data-date-format')) || 'Y-m-d H:i:S',
            onOpen: function (selectedDates, dateStr, instance) {
              if (!el.value) {
                var now = new Date();
                now.setSeconds(0, 0);
                instance.setDate(now, true);
              }
            },
            onChange: function () {
              notifyFilterChange();
            }
          });
          el.dataset.faInitialized = '1';
          return true;
        case 'datepicker':
          if (!window.flatpickr) return true;
          flatpickr(el, {
            enableTime: false,
            dateFormat: toFlatpickrFormat(el.getAttribute('data-date-format')) || 'Y-m-d',
            onChange: function () {
              notifyFilterChange();
            }
          });
          el.dataset.faInitialized = '1';
          return true;
        case 'timepicker':
          if (!window.flatpickr) return true;
          flatpickr(el, {
            enableTime: true,
            noCalendar: true,
            time_24hr: true,
            enableSeconds: hasSeconds(el.getAttribute('data-date-format')),
            minuteIncrement: 1,
            dateFormat: toFlatpickrFormat(el.getAttribute('data-date-format')) || 'H:i:S',
            onChange: function () {
              notifyFilterChange();
            }
          });
          el.dataset.faInitialized = '1';
          return true;
        case 'datetimerangepicker':
          if (!window.flatpickr) return true;
          flatpickr(el, {
            mode: 'range',
            enableTime: true,
            time_24hr: true,
            enableSeconds: hasSeconds(el.getAttribute('data-date-format')),
            minuteIncrement: 1,
            dateFormat: toFlatpickrFormat(el.getAttribute('data-date-format')) || 'Y-m-d H:i:S',
            locale: { rangeSeparator: ' - ' },
            onChange: function () {
              notifyFilterChange();
            }
          });
          el.dataset.faInitialized = '1';
          return true;
        case 'daterangepicker':
          if (!window.flatpickr) return true;
          flatpickr(el, {
            mode: 'range',
            enableTime: false,
            dateFormat: toFlatpickrFormat(el.getAttribute('data-date-format')) || 'Y-m-d',
            locale: { rangeSeparator: ' - ' },
            onChange: function () {
              notifyFilterChange();
            }
          });
          el.dataset.faInitialized = '1';
          return true;
        case 'timerangepicker':
          if (!window.flatpickr) return true;
          flatpickr(el, {
            mode: 'range',
            enableTime: true,
            noCalendar: true,
            time_24hr: true,
            enableSeconds: hasSeconds(el.getAttribute('data-date-format')),
            minuteIncrement: 1,
            dateFormat: toFlatpickrFormat(el.getAttribute('data-date-format')) || 'H:i:S',
            locale: { rangeSeparator: ' - ' },
            onChange: function () {
              notifyFilterChange();
            }
          });
          el.dataset.faInitialized = '1';
          return true;
        case 'leaflet':
          processLeafletWidget(el, name);
          el.dataset.faInitialized = '1';
          return true;
        // x-editable* widgets are handled natively by editable.js (Editable module).
        // The old jQuery x-editable cases are intentionally no-ops.
        case 'x-editable':
        case 'x-editable-combodate':
        case 'x-editable-select-multiple':
        case 'x-editable-boolean':
          el.dataset.faInitialized = '1';
          return true;
      }
    };

    this.addInlineModelRow = function (field) {
      var template = field.querySelector('.inline-model-row-template');
      var rows = field.querySelector('.inline-model-rows');
      if (!template || !rows) return;

      var index = parseInt(field.dataset.nextIndex, 10);
      if (Number.isNaN(index)) index = 0;
      rows.querySelectorAll('[data-inline-row]').forEach(function (existingRow) {
        var match = existingRow.dataset.prefix.match(/-(\d+)-$/);
        if (match) index = Math.max(index, parseInt(match[1], 10) + 1);
      });
      field.dataset.nextIndex = String(index + 1);
      var row = template.content.firstElementChild.cloneNode(true);
      var marker = '__prefix__';
      var prefix = field.dataset.relationship + '-' + index + '-';
      row.querySelectorAll('*').forEach(function (node) {
        Array.from(node.attributes).forEach(function (attribute) {
          if (attribute.value.indexOf(marker) !== -1) {
            node.setAttribute(
              attribute.name,
              attribute.value.split(marker).join(String(index))
            );
          }
        });
      });
      row.dataset.prefix = prefix;
      rows.appendChild(row);
      if (field.dataset.isCollection !== 'true') {
        var addButton = field.querySelector('[data-inline-add]');
        if (addButton) addButton.disabled = true;
      }
      var firstInput = row.querySelector('input:not([type="hidden"]), select, textarea');
      if (firstInput) firstInput.focus();
      this.applyGlobalStyles(row);
    };

    this.saveInlineModelRow = function (row) {
      var field = row.closest('[data-inline-model]');
      if (!field) return;
      var prefix = row.dataset.prefix;
      var values = {};
      row.querySelectorAll('input[name], select[name], textarea[name]').forEach(function (input) {
        if (input.disabled || !input.name.startsWith(prefix)) return;
        var name = input.name.slice(prefix.length);
        if (!name) return;
        if (input.type === 'checkbox' && !input.checked) return;
        if (input.type === 'radio' && !input.checked) return;
        var value = input.type === 'checkbox' ? input.value || 'y' : input.value;
        if (input instanceof HTMLSelectElement && input.multiple) {
          value = Array.from(input.selectedOptions).map(function (option) { return option.value; });
        }
        if (Object.prototype.hasOwnProperty.call(values, name)) {
          if (!Array.isArray(values[name])) values[name] = [values[name]];
          values[name].push(value);
        } else {
          values[name] = value;
        }
      });

      return this.sendInlineModelRequest(field, row, {
        action: 'save',
        parent_id: field.dataset.parentId,
        child_id: row.dataset.childId ? JSON.parse(row.dataset.childId) : null,
        prefix: prefix,
        csrf_token: values[field.dataset.csrfField] || '',
        values: values
      });
    };

    this.deleteInlineModelRow = function (row) {
      var field = row.closest('[data-inline-model]');
      if (!field) return;
      if (!row.dataset.childId) {
        row.remove();
        if (field.dataset.isCollection !== 'true') {
          var addButton = field.querySelector('[data-inline-add]');
          if (addButton) addButton.disabled = false;
        }
        return Promise.resolve();
      }
      if (!window.confirm(field.dataset.deleteMessage || 'Delete this related record?')) {
        return Promise.resolve();
      }
      var csrfName = field.dataset.csrfField;
      var csrfInput = Array.from(row.querySelectorAll('input[type="hidden"]')).find(function (input) {
        return input.name === row.dataset.prefix + csrfName;
      });
      return this.sendInlineModelRequest(field, row, {
        action: 'delete',
        parent_id: field.dataset.parentId,
        child_id: JSON.parse(row.dataset.childId),
        prefix: row.dataset.prefix,
        csrf_token: csrfInput ? csrfInput.value : ''
      }).then(function () {
        row.remove();
        if (field.dataset.isCollection !== 'true') {
          var addButton = field.querySelector('[data-inline-add]');
          if (addButton) addButton.disabled = false;
        }
      });
    };

    this.sendInlineModelRequest = function (field, row, data) {
      var self = this;
      var status = row.querySelector('.inline-model-status');
      var buttons = row.querySelectorAll('button');
      buttons.forEach(function (button) { button.disabled = true; });
      if (status) status.textContent = '';

      return fetch(field.dataset.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (response) {
        return response.json().catch(function () {
          return { error: response.statusText };
        }).then(function (payload) {
          if (!response.ok) throw new Error(payload.error || JSON.stringify(payload.errors || payload));
          return payload;
        });
      }).then(function (payload) {
        if (payload.child_id !== undefined) {
          row.dataset.childId = JSON.stringify(payload.child_id);
          var field = row.closest('[data-inline-model]');
          if (field && field.dataset.isCollection !== 'true') {
            var addButton = field.querySelector('[data-inline-add]');
            if (addButton) addButton.disabled = true;
          }
        }
        if (status) status.textContent = payload.message || 'Saved.';
        return payload;
      }).catch(function (error) {
        if (status) status.textContent = error.message;
        throw error;
      }).finally(function () {
        buttons.forEach(function (button) { button.disabled = false; });
      });
    };

    /**
    * Apply global input styles.
    *
    * @method applyGlobalStyles
    * @param {Element} parent DOM element
    */
    this.applyGlobalStyles = function (parent, isModal) {
      var self = this;
      parent.querySelectorAll('input[data-role], select[data-role], textarea[data-role], button[data-role], a[data-role]').forEach(function (el) {
        self.applyStyle(el, el.getAttribute('data-role'), isModal ? parent : null);
      });
    };

    /**
    * Add a field converter for customizing styles
    *
    * @method addFieldConverter
    * @param {converter} function(el, name)
    */
    this.addFieldConverter = function (converter) {
      fieldConverters.push(converter);
    };
  };

  document.addEventListener('click', function (event) {
    var target = event.target.closest('[data-inline-add], [data-inline-save], [data-inline-delete]');
    if (!target) return;
    if (target.hasAttribute('data-inline-add')) {
      faForm.addInlineModelRow(target.closest('[data-inline-model]'));
    } else if (target.hasAttribute('data-inline-save')) {
      faForm.saveInlineModelRow(target.closest('[data-inline-row]')).catch(function () {});
    } else {
      faForm.deleteInlineModelRow(target.closest('[data-inline-row]')).catch(function () {});
    }
  });

  document.addEventListener('submit', function (event) {
    var form = event.target;
    if (!form.matches('form[data-ajax-create-url]')) return;
    event.preventDefault();
    var submit = form.querySelector('[type="submit"]');
    if (submit) submit.disabled = true;
    var errorBox = form.querySelector('.ajax-form-error');
    if (!errorBox) {
      errorBox = document.createElement('div');
      errorBox.className = 'alert alert-danger ajax-form-error';
      errorBox.setAttribute('role', 'alert');
      form.prepend(errorBox);
    }
    errorBox.textContent = '';
    fetch(form.dataset.ajaxCreateUrl, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
      .then(function (response) {
        return response.json().then(function (payload) {
          if (!response.ok) throw new Error(payload.error || JSON.stringify(payload.errors || payload));
          return payload;
        });
      })
      .then(function (payload) { window.location.href = payload.redirect_url; })
      .catch(function (error) { errorBox.textContent = error.message; if (submit) submit.disabled = false; });
  });

  // Expose faForm globally
  var faForm = window.faForm = new AdminForm();
  document.dispatchEvent(new Event('adminFormReady'));

  // Apply global styles for current page after page loaded
  function applyOnReady() {
    faForm.applyGlobalStyles(document);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyOnReady);
  } else {
    applyOnReady();
  }
})();