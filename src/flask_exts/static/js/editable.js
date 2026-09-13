import { createModal } from './ui-factory.js'
import FieldRegistry from './field-registry.js';

/* ================================================================
InlineEdit — Pure JS implementation, framework-agnostic
Example:
  const editor = new Editable({
    onSuccess: (target, value,) => {
      console.log()
    }
  })
// ================================================================*/

class Editable {
  constructor(options = {}) {
    // Default configuration
    this.options = {
      selector: ".editable",
      onSave: null,        // Custom save handler (url, value) => Promise<{success, value?, message?}>
      onSuccess: null,     // Success callback (target, value, message) => void
      saveOptions: {},     // Default save options, e.g. { method: 'POST', dataType: 'json' }
      ...options
    }

    this.fieldPluginRegistry = new FieldRegistry()
    this.fieldPluginRegistry.registerBuiltins();

    // Create modal and overlay elements
    const { overlay, titleEl, body, errorEl, cancelButton, saveButton } = createModal()
    this.overlay = overlay
    this.modalTitle = titleEl
    this.modalBody = body
    this.errorAlert = errorEl
    this.cancelButton = cancelButton
    this.saveButton = saveButton
    this.modal = new bootstrap.Modal(overlay, { backdrop: true, keyboard: true, focus: true });
    document.body.appendChild(this.overlay)
    // bind events to the modal buttons
    this.bindEvents()
    // set up initial state of the editor u
    this.originalValue = ""
    this.activeTarget = null
    this.fieldType = "text"
    this.field = null
    this.saving = false
    // bind events to the editable elements
    this.bindEditables()
  }

  // --------- Field management ----------
  resolveFieldType() {
    return this.fieldPluginRegistry.normalizeType(this.activeTarget.dataset?.type)
  }

  createField() {
    if (this.fieldType === "select") {
      const options = this.fieldPluginRegistry.parseOptions(this.fieldType, this.activeTarget.dataset?.options)
      this.selectOptions = options
      return this.fieldPluginRegistry.createField(this.fieldType, { options })
    }
    else {
      return this.fieldPluginRegistry.createField(this.fieldType)
    }
  }

  getFieldValue() {
    return this.fieldPluginRegistry.getValue(this.fieldType, this.field)
  }

  setFieldValue(value) {
    this.fieldPluginRegistry.setValue(this.fieldType, this.field, value)
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
    this.overlay.addEventListener('shown.bs.modal', () => {
      if (this.activeTarget) {
        this.activeTarget.classList.add("editing")
      }
      this._hideError();
    });
    this.overlay.addEventListener('hidden.bs.modal', () => {
      if (this.activeTarget) {
        this.activeTarget.classList.remove("editing")
        this.activeTarget.focus();
      }
      this._hideError();
    });
  }

  // --------- Open / Close / Save ----------
  open(target) {
    this.originalValue = target.dataset.Value ?? target.textContent.trim()
    if (this.activeTarget && this.activeTarget == target) {
    } else {
      this.activeTarget = target
      this.modalTitle.textContent = target.dataset.Title ?? "✎"
      if (this.field) {
        this.field.remove()
      }
      this.fieldType = this.resolveFieldType()
      this.field = this.createField()
      this.setFieldValue(this.originalValue)
      this.modalBody.prepend(this.field)
    }
    this.modal.show();
    this.field.focus();
  }

  close() {
    if (this.saving) return
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

    const url = this.activeTarget.dataset.url
    const saveFn = this.options.onSave || this.defaultSave
    this.saving = true
    try {
      const data = {
        pk: this.activeTarget.dataset.pk,
        [this.activeTarget.dataset.name]: fieldValue,
        csrf_token: this.activeTarget.dataset.csrf
      }
      const result = await saveFn(url, data, this.options.saveOptions)
      if (result.success) {
        const newValue = fieldValue
        const displayValue = String(newValue)
        this.activeTarget.dataset.value = newValue
        if (this.fieldType === "select") {
          const label = this.getSelectLabel(newValue)
          this.activeTarget.textContent = label
        } else {
          this.activeTarget.textContent = displayValue
        }
        this.saving = false
        this.close()
        if (this.options.onSuccess) {
          this.options.onSuccess(this.activeTarget, newValue, result.message)
        }
      } else {
        this._showError(result.message)
      }
    } catch (e) {
      this._showError("Network error, please retry")
      console.error("InlineEdit save error:", e)
    } finally {
      this.saving = false
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
  async defaultSave(url, data, options = {}) {
    if (!url) return { success: true, value: data }

    const { method = 'POST', headers = { 'Content-Type': 'application/json' }, timeout = 10000 } = options;

    const fetchOptions = {
      method,
      headers: { 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify(data),
      signal: AbortSignal.timeout(timeout)
    };

    try {
      const response = await fetch(url, fetchOptions);
      let responseData;
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        responseData = await response.json();
      } else {
        responseData = await response.text();
      }

      if (!response.ok) {
        const message = responseData?.message || responseData?.error || `${response.status} ${response.statusText}`;
        return { success: false, message };
      }

      return { success: true, message: responseData?.message ?? responseData };
    } catch (error) {
      return { success: false, message: error.message || 'Network error', };
    }
  }

  getSelectLabel(value) {
    if (!this.selectOptions) return value
    const option = this.selectOptions.find(opt => String(opt.value) === String(value))
    return option ? option.label : value
  }
}

export default Editable
