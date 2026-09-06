import {
  createInputField,
  createTextareaField,
  createSelectField,
  createSwitchField,
  createModal,
} from './ui-factory.js'

class FieldRegistry {
  constructor() {
    this.plugins = new Map()
  }

  register(plugin) {
    this.plugins.set(plugin.type, plugin)
    return plugin
  }

  registerMany(plugins) {
    plugins.forEach(p => this.register(p))
  }

  registerBuiltins() {
    builtinFieldPlugins.forEach(p => this.register(p))
  }

  _resolve(type) {
    return this.plugins.get(type) || this.plugins.get("text")
  }

  normalizeType(type) {
    const key = String(type ?? "text").toLowerCase()
    return this.plugins.has(key) ? key : "text"
  }

  createField(type, params = {}) {
    const plugin = this._resolve(type)
    return plugin.createField(params)
  }

  setValue(type, field, value) {
    const plugin = this._resolve(type)
    plugin.setValue(field, value)
  }

  getValue(type, field) {
    const plugin = this._resolve(type)
    return plugin.getValue(field)
  }

  parseOptions(type, source) {
    const plugin = this._resolve(type)
    if (typeof plugin.parseOptions === "function") {
      return plugin.parseOptions(source)
    }
  }
}

const builtinFieldPlugins = [
  {
    type: "text",
    createField(params = {}) {
      return createInputField({ type: "text" })
    },
    setValue(field, value) {
      field.value = String(value ?? "")
    },
    getValue(field) {
      return field.value.trim()
    }
  },
  {
    type: "number",
    createField(params = {}) {
      return createInputField({ type: "number" })
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
    createField(params = {}) {
      return createInputField({ type: "email" })
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
    createField(params = {}) {
      return createInputField({ type: "date" })
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
    createField(params = {}) {
      return createTextareaField({ className: "w-100" })
    },
    setValue(field, value) {
      field.value = String(value ?? "")
    },
    getValue(field) {
      return field.value.trim()
    }
  },
  {
    type: "check",
    createField(params = {}) {
      const field = createInputField({ type: "checkbox" })
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
    type: "switch",
    createField(params = {}) {
      return createSwitchField()
    },
    setValue(field, value) {
      const checkbox = field.querySelector('input[type="checkbox"]');
      checkbox.checked = String(value ?? "").toLowerCase() === "true"
    },
    getValue(field) {
      const checkbox = field.querySelector('input[type="checkbox"]');
      return checkbox.checked
    }
  },
  {
    type: "select",
    createField({ options = [] } = {}) {
      return createSelectField({ options })
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
    parseOptions(source) {
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
  }
]

export default FieldRegistry;
