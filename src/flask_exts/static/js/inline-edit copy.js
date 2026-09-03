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
    const key = String(type ?? "text").toLowerCase()
    return this.plugins.get(key) || this.plugins.get("text")
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

  buildOptions(type, target, field, originalValue) {
    const plugin = this._resolve(type)
    if (typeof plugin.buildOptions === "function") {
      plugin.buildOptions(target, field, originalValue)
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
    buildOptions(target, field, originalValue) {
      const raw = target.dataset.options || ""
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

      const options = parseOptions(raw)
      field.innerHTML = ""

      if (!options.length) {
        const fallback = document.createElement("option")
        fallback.value = String(originalValue ?? "")
        fallback.textContent = String(originalValue ?? "")
        field.appendChild(fallback)
        return
      }

      options.forEach(({ label, value }) => {
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
      onSuccess: null,     // Success callback (value, target) => void
      onError: null,       // Error callback  (message, target) => void
      ...options
    }

    this.fieldPluginRegistry = new FieldPluginRegistry()
    this.fieldPluginRegistry.registerMany(builtinFieldPlugins)

    this.overlay = document.querySelector(this.options.overlaySelector)
    if (!this.overlay) {
      this.overlay = this.createOverlay()
    }

    this.errorEl = document.querySelector(this.options.errorSelector)
    if (!this.errorEl) {
      this.errorEl = this.createErrorEl()
    }

    this.activeTarget = null
    this.fieldType = "text"
    this.field = null    
    this.originalValue = ""    
    this.saving = false
    this.bindEditables()    
  }

  createFieldByType(type = "text") {
    return this.fieldPluginRegistry.createField(type)
  }

  normalizeFieldType(type) {
    return this.fieldPluginRegistry.normalizeType(type)
  }

  setFieldValue(value) {
    this.fieldPluginRegistry.setValue(this.fieldType, this.field, value)
  }

  buildFieldOptions(target) {
    this.fieldPluginRegistry.buildOptions(this.fieldType, target, this.field, this.originalValue)
  }

  getFieldValue() {
    return this.fieldPluginRegistry.getValue(this.fieldType, this.field)
  }

  createOverlay(type = "text") {
    const overlay = document.createElement("div")
    overlay.className = "inline-edit-overlay"

    const actions = this.createActions()
    overlay.append(this.createFieldByType(type), actions)
    document.body.appendChild(overlay)
    return overlay
  }

  setActiveFieldType(type) {
    const normalizedType = this.normalizeFieldType(type)
    const existingField = this.overlay.querySelector(".inline-edit-field")
    this.fieldType = normalizedType

    if (existingField) {
      existingField.remove()
    }

    const field = this.createFieldByType(this.fieldType)
    const actions = this.overlay.querySelector(".actions")
    this.overlay.insertBefore(field, actions)
    this.field = field
    return field
  }

  createActions() {
    const actions = document.createElement("div")
    actions.className = "actions"
    const confirmBtn = document.createElement("button")
    confirmBtn.className = "confirm-btn"
    confirmBtn.textContent = "✓"
    confirmBtn.addEventListener("click", () => this.save())
    const cancelBtn = document.createElement("button")
    cancelBtn.className = "cancel-btn"
    cancelBtn.textContent = "✗"
    cancelBtn.addEventListener("click", () => this.cancel())
    actions.append(confirmBtn, cancelBtn)
    return actions
  }

  createErrorEl() {
    const errorElm = document.createElement("div")
    errorElm.className = "inline-edit-error"
    document.body.appendChild(errorElm)
    return errorElm
  }

  // ---------- Initialize bindings ----------

  bindEditables() {
    document.querySelectorAll(this.options.selector).forEach(el => {
      if (el.dataset.inlineBound === "true") return
      el.dataset.inlineBound = "true"
      el.addEventListener("click", () => this.open(el))
    })
  }

  bindFieldEvents() {
    const field = this.field
    if (!field || field.dataset.inlineBound === "true") return
    field.dataset.inlineBound = "true"

    const handleKeydown = (e) => {
      if (e.key === "Escape") { e.preventDefault(); this.cancel() }
      if (e.key === "Enter") {
        if (this.fieldType === "textarea" && e.ctrlKey) {
          e.preventDefault(); this.save()
        } else if (this.fieldType !== "textarea" && this.fieldType !== "select") {
          e.preventDefault(); this.save()
        }
      }
    }

    const handleBlur = () => {
      setTimeout(() => {
        if (!this.saving && !this.overlay.contains(document.activeElement)) {
          this.cancel()
        }
      }, 150)
    }

    field.addEventListener("keydown", handleKeydown)
    field.addEventListener("blur", handleBlur)

    if (this.fieldType === "bool") {
      field.addEventListener("change", () => {
        this.setFieldValue(String(field.checked))
      })
    }
  }

  

  _resolveFieldType(target) {
    const type = this.normalizeFieldType(target?.dataset?.type)
    if (type !== "text") return type
    return target?.dataset?.editMultiline === "true" ? "textarea" : "text"
  }

  open(target) {
    if (this.activeTarget && this.activeTarget !== target) this.cancel()

    this.activeTarget = target
    this.fieldType = this._resolveFieldType(target)
    this.originalValue = target.dataset.editValue ?? target.textContent.trim()

    this.setActiveFieldType(this.fieldType)
    this.setFieldValue(this.originalValue)
    this.buildFieldOptions(target)
    this.bindFieldEvents()

    target.classList.add("editing")
    this._positionOverlay(target)
    this.overlay.classList.add("active")

    requestAnimationFrame(() => {
      const field = this._getActiveField()
      if (!field) return
      field.focus()
      if (field.tagName !== "INPUT" || field.type !== "checkbox") {
        field.select?.()
      }
    })
  }

  _getActiveField() {
    return this.field
  }

  async save() {
    if (this.saving) return

    const newValue = this.getFieldValue()
    const originalValue = this.fieldType === "bool"
      ? String(this.originalValue ?? "").toLowerCase() === "true"
      : this.originalValue

    if (newValue === originalValue) {
      this.close()
      return
    }

    this.saving = true
    this.overlay.classList.add("saving")
    this._hideError()

    try {
      const url = this.activeTarget.dataset.editUrl
      const failOn = this.activeTarget.dataset.editFailOn
      const saveFn = this.options.onSave || this._defaultSave.bind(this)
      const result = await saveFn(url, newValue, failOn)

      if (result.success) {
        const serverValue = result.value ?? newValue
        const displayValue = typeof serverValue === "boolean" ? String(serverValue) : serverValue
        this.activeTarget.textContent = displayValue
        this.activeTarget.dataset.editValue = String(displayValue)
        if (this.options.onSuccess) {
          this.options.onSuccess(serverValue, this.activeTarget)
        }
        this.close()
      } else {
        this._showError(result.message || "Save failed")
        if (this.options.onError) {
          this.options.onError(result.message, this.activeTarget)
        }
      }
    } catch (e) {
      this._showError("Network error, please retry")
    } finally {
      this.saving = false
      this.overlay.classList.remove("saving")
    }
  }

  cancel() {
    this._hideError()
    this.close()
  }

  close() {
    if (this.activeTarget) this.activeTarget.classList.remove("editing")
    this.overlay.classList.remove("active")
    this.activeTarget = null
  }





  _positionOverlay(target) {
    const rect = target.getBoundingClientRect()
    this.overlay.style.top = `${rect.top - 4}px`
    this.overlay.style.left = `${rect.right + 8}px`
    if (rect.right + 8 + 350 > window.innerWidth) {
      this.overlay.style.left = `${rect.left}px`
      this.overlay.style.top = `${rect.bottom + 4}px`
    }
  }

  // Built-in mock AJAX (can be replaced by options.onSave) 
  async _defaultSave(url, value, failOn) {
    console.log(`[AJAX] POST ${url} → { value: "${value}" }`)
    await new Promise(r => setTimeout(r, 600))

    if (failOn && value === failOn) {
      return { success: false, message: `"${value}" is invalid and rejected by the server` }
    }
    return { success: true, value }

    // ===== Replace with actual project code ===== 
    // const res = await fetch(url, {
    //   method: "PATCH",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({ value })
    // })
    // const data = await res.json()
    // return res.ok
    //   ? { success: true, value: data.value }
    //   : { success: false, message: data.message }
  }

  _showError(message) {
    const rect = this.overlay.getBoundingClientRect()
    this.errorEl.textContent = message
    this.errorEl.style.top = `${rect.bottom + 4}px`
    this.errorEl.style.left = `${rect.left}px`
    this.errorEl.classList.add("active")
  }

  _hideError() {
    this.errorEl.classList.remove("active")
  }
}

export default InlineEdit
