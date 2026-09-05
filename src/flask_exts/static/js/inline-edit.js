class FieldPluginRegistry {
  constructor() {
    this.plugins = new Map()
  }

  register(plugin) {
    this.plugins.set(plugin.type, plugin)
    return plugin
  }

  registerMany(plugins) {
    plugins.forEach(plugin => this.register(plugin))
  }

  _resolve(type) {
    return this.plugins.get(type) || this.plugins.get("text")
  }

  normalizeType(type) {
    const key = String(type ?? "text").toLowerCase()
    return this.plugins.has(key) ? key : "text"
  }

  createField(type) {
    const plugin = this._resolve(type)
    return plugin.createField()
  }

  setValue(type, field, value) {
    const plugin = this._resolve(type)
    plugin.setValue(field, value)
  }

  getValue(type, field) {
    const plugin = this._resolve(type)
    return plugin.getValue(field)
  }

  buildOptions(type, field, options, originalValue) {
    const plugin = this._resolve(type)
    if (typeof plugin.buildOptions === "function") {
      plugin.buildOptions(field, options, originalValue)
    }
  }
}

const createInputField = (type, className, attributes = {}) => {
  const field = document.createElement("input")
  field.type = type
  field.className = className
  Object.entries(attributes).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      field.setAttribute(key, String(value))
    }
  })
  return field
}

const createTextareaField = (className, attributes = {}) => {
  const field = document.createElement("textarea")
  field.className = className
  Object.entries(attributes).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      field.setAttribute(key, String(value))
    }
  })
  return field
}

const createSelectField = (className) => {
  const field = document.createElement("select")
  field.className = className
  return field
}


const builtinFieldPlugins = [
  {
    type: "text",
    createField() {
      return createInputField("text", "inline-edit-field inline-edit-input")
    },
    setValue(field, value) {
      field.value = String(value ?? "")
    },
    getValue(field) {
      return field.value.trim()
    }
  },
  {
    type: "textarea",
    createField() {
      return createTextareaField("inline-edit-field inline-edit-textarea")
    },
    setValue(field, value) {
      field.value = String(value ?? "")
    },
    getValue(field) {
      return field.value.trim()
    }
  },
  {
    type: "bool",
    createField() {
      const field = createInputField("checkbox", "inline-edit-field inline-edit-bool", {
        "aria-label": "boolean toggle"
      })
      return field
    },
    setValue(field, value) {
      field.checked = String(value ?? "").toLowerCase() === "true"
    },
    getValue(field) {
      return field.checked
    }
  },

  {
    type: "number",
    createField() {
      return createInputField("number", "inline-edit-field inline-edit-number")
    },
    setValue(field, value) {
      field.value = String(value ?? "")
    },
    getValue(field) {
      return Number(field.value)
    }
  },

  {
    type: "email",
    createField() {
      return createInputField("email", "inline-edit-field inline-edit-email")
    },
    setValue(field, value) {
      field.value = String(value ?? "")
    },
    getValue(field) {
      return field.value.trim()
    }
  },

  {
    type: "date",
    createField() {
      return createInputField("date", "inline-edit-field inline-edit-date")
    },
    setValue(field, value) {
      field.value = String(value ?? "")
    },
    getValue(field) {
      return field.value.trim()
    }
  },

  {
    type: "select",
    createField() {
      return createSelectField("inline-edit-field inline-edit-select")
    },
    setValue(field, value) {
      const options = Array.from(field.options).map(option => option.value)
      if (options.includes(String(value ?? ""))) {
        field.value = String(value ?? "")
      } else if (field.options.length > 0) {
        field.value = field.options[0].value
      }
    },
    getValue(field) {
      return field.value
    },
    buildOptions(field, options, originalValue) {
      const raw = options || ""
      if (!raw) {
        field.innerHTML = ""
        const fallback = document.createElement("option")
        fallback.value = String(originalValue ?? "")
        fallback.textContent = String(originalValue ?? "")
        field.appendChild(fallback)
        return
      }

      const parseOptions = (source) => {
        if (!source) return []
        try {
          const parsed = JSON.parse(source)
          if (Array.isArray(parsed)) return parsed
        } catch (e) {
          // Fallback to string parsing below
        }

        return source.split(",").map(item => {
          const trimmed = item.trim()
          if (!trimmed) return null
          if (trimmed.includes("|")) {
            const [label, value] = trimmed.split("|").map(part => part.trim())
            return { label: label || value, value: value || label }
          }
          return { label: trimmed, value: trimmed }
        }).filter(Boolean)
      }

      const rawptions = parseOptions(raw)
      field.innerHTML = ""

      if (!rawptions.length) {
        const fallback = document.createElement("option")
        fallback.value = String(originalValue ?? "")
        fallback.textContent = String(originalValue ?? "")
        field.appendChild(fallback)
        return
      }

      rawptions.forEach(({ label, value }) => {
        const option = document.createElement("option")
        option.value = value
        option.textContent = label
        field.appendChild(option)
      })

      const current = String(originalValue ?? "")
      if (Array.from(field.options).some(option => option.value === current)) {
        field.value = current
      }
    }
  },
]

function createOverlay(title = "", cancelText = "✗", saveText = "✓") {
  const overlay = document.createElement("div");
  overlay.className = "modal fade";
  overlay.tabIndex = -1;

  const dialog = document.createElement('div');
  dialog.className = 'modal-dialog';
  overlay.appendChild(dialog);

  const content = document.createElement('div');
  content.className = 'modal-content';
  dialog.appendChild(content);

  if (title) {
    const header = document.createElement('div');
    header.className = 'modal-header';
    content.appendChild(header);
    const modalTitle = document.createElement('h5');
    modalTitle.className = 'modal-title';
    modalTitle.textContent = title;
    header.appendChild(modalTitle);
  }

  const body = document.createElement('div');
  body.className = 'modal-body';
  content.appendChild(body);

  const error = document.createElement('div');
  error.className = 'alert alert-danger d-none';
  body.appendChild(error);

  const footer = document.createElement('div');
  footer.className = 'modal-footer';
  content.appendChild(footer);

  const cancelButton = document.createElement('button');
  cancelButton.type = 'button';
  cancelButton.className = 'btn btn-secondary';
  cancelButton.setAttribute('data-bs-dismiss', 'modal');
  cancelButton.textContent = cancelText;
  footer.appendChild(cancelButton);

  const saveButton = document.createElement('button');
  saveButton.type = 'button';
  saveButton.className = 'btn btn-primary';
  saveButton.textContent = saveText;
  footer.appendChild(saveButton);

  return { overlay, body, error, cancelButton, saveButton };
}

// ================================================================
// InlineEdit — Pure JS implementation, framework-agnostic
// ================================================================
class InlineEdit {
  constructor(options = {}) {
    // Default configuration
    this.options = {
      selector: ".editable",
      overlaySelector: ".inline-edit-overlay",
      errorSelector: ".inline-edit-error",
      onSave: null,        // Custom save handler (url, value) => Promise<{success, value?, message?}>
      onSuccess: null,     // Success callback (target, value) => void
      ...options
    }

    this.fieldPluginRegistry = new FieldPluginRegistry()
    this.fieldPluginRegistry.registerMany(builtinFieldPlugins);

    const { overlay, body, error, cancelButton, saveButton } = createOverlay()
    this.overlay = overlay
    this.modalBody = body
    this.errorAlert = error
    this.cancelButton = cancelButton
    this.saveButton = saveButton
    document.body.appendChild(this.overlay)

    this.bindEvents()

    this.originalValue = ""
    this.activeTarget = null
    this.fieldType = "text"
    this.field = null
    this.saving = false
    // 
    this.bindEditables()
    // Initialize Bootstrap modal
    this.modal = new bootstrap.Modal(this.overlay)
  }

  // --------- Field management ----------
  resolveFieldType() {
    return this.fieldPluginRegistry.normalizeType(this.activeTarget.dataset?.type)
  }

  createField() {
    const field = this.fieldPluginRegistry.createField(this.fieldType)
    this.fieldPluginRegistry.setValue(this.fieldType, field, this.originalValue)
    this.fieldPluginRegistry.buildOptions(this.fieldType, field, this.activeTarget.dataset.options, this.originalValue)
    return field
  }

  getFieldValue() {
    return this.fieldPluginRegistry.getValue(this.fieldType, this.field)
  }

  _showError(message) {
    this.errorAlert.textContent = message
    this.errorAlert.classList.remove('d-none');
  }

  _hideError() {
    this.errorAlert.textContent = ""
    this.errorAlert.classList.add('d-none');
  }

  // ---------- Initialize bindings ----------

  bindEditables() {
    document.querySelectorAll(this.options.selector).forEach(el => {
      el.addEventListener("click", () => this.open(el))
    })
  }

  bindEvents() {
    this.overlay.addEventListener("keydown", (e) => this.handleKeydown(e))
    this.cancelButton.addEventListener("click", (e) => { e.preventDefault(); this.close() })
    this.saveButton.addEventListener("click", (e) => { e.preventDefault(); this.save() })

    // Blur the active element when the modal is hidden to prevent focus issues
    this.overlay.addEventListener('hide.bs.modal', () => {
      if (this.overlay.contains(document.activeElement)) {
        document.activeElement.blur();
      }
    });
    this.overlay.addEventListener('hidden.bs.modal', () => {
      if (this.activeTarget) {
        this.activeTarget.focus();
      }
      this._hideError();
    });
  }

  // --------- Open / Close / Save ----------
  open(target) {
    target.classList.add("editing")
    this.originalValue = target.dataset.editValue ?? target.textContent.trim()

    if (this.activeTarget && this.activeTarget == target) {
    } else {
      this.activeTarget = target
      if (this.field) {
        this.field.remove()
      }
      this.fieldType = this.resolveFieldType()
      this.field = this.createField()
      this.modalBody.prepend(this.field)
    }

    this.modal.show();
    this.field.focus();
  }

  close() {
    if (this.saving) return
    this.activeTarget.classList.remove("editing")
    this.modal.hide()
  }

  async save() {
    if (this.saving) return;

    const fieldValue = this.getFieldValue()
    if (fieldValue === this.originalValue) {
      this.close()
      return;
    }


    this.overlay.classList.add("saving")
    this._hideError()

    const url = this.activeTarget.dataset.editUrl
    const saveFn = this.options.onSave || this._defaultSave

    try {
      this.saving = true
      const result = await saveFn(url, fieldValue)
      this.saving = false

      if (result.success) {
        const newValue = result.value
        const displayValue = String(newValue)
        this.activeTarget.textContent = displayValue
        this.activeTarget.dataset.editValue = displayValue
        if (this.options.onSuccess) {
          this.options.onSuccess(this.activeTarget, newValue)
        }
        this.close()
      } else {
        this._showError(result.message)
      }
    } catch (e) {
      this._showError("Network error, please retry")
    } finally {

      this.overlay.classList.remove("saving")
    }
  }

  handleKeydown = (e) => {
    if (e.key === "Escape") { e.preventDefault(); this.close() }
    if (e.key === "Enter") {
      if (this.fieldType === "textarea" && e.ctrlKey) {
        e.preventDefault(); this.save()
      } else if (this.fieldType !== "textarea" && this.fieldType !== "select") {
        e.preventDefault(); this.save()
      }
    }
  }


  // Default save function (can be replaced by options.onSave)  
  async _defaultSave(url, value, options = {}) {
    if (!url) {
      return { success: true, value }
    }

    const {
      method = 'POST',
      headers = {},
      timeout = 10000,
    } = options;

    const fetchOptions = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      body: JSON.stringify({ value }),
      signal: AbortSignal.timeout(timeout)
    };

    try {
      const response = await fetch(url, fetchOptions);
      let responseData;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        responseData = await response.text();
      }

      if (!response.ok) {
        const message = `${response.status} ${response.statusText}`;
        return { success: false, message };
      }

      return { success: true, value: responseData };

    } catch (error) {
      console.error('_defaultSave error:', error);
      return {
        success: false,
        message: error.message || 'Network error',
      };
    }
  }
}

export default InlineEdit
