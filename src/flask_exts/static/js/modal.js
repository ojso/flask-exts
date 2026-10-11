/**
 * ModalForm
 * ---------
 * A reusable, configuration-driven modal form component built on top of
 * Bootstrap 5's Modal. It reads its configuration from a trigger element's
 * `data-*` attributes, dynamically renders a form inside a Bootstrap modal,
 * validates input on the client, submits it via a caller-supplied `fetch`
 * implementation, and invokes caller-provided callbacks on success or failure.
 *
 * This class is UI-binding agnostic: it does NOT attach any event listeners
 * to trigger elements. Callers are responsible for wiring up events (e.g. via
 * `document.querySelectorAll(selector).forEach(...)`) and for providing the
 * `onSuccess` / `onError` callbacks and the `fetchImpl`.
 *
 * All user-facing strings are centralized in `DEFAULT_MESSAGES` and can be
 * partially overridden via `options.messages`.
 *
 * @example
 *   // 1. Markup
 *   // <button class="js-form-trigger"
 *   //   data-url="/api/users"
 *   //   data-method="POST"
 *   //   data-title="Create User"
 *   //   data-submit-text="Create"
 *   //   data-fields='[{"name":"username","label":"Username","required":true}]'>
 *   //   Create User
 *   // </button>
 *
 *   // 2. Bind events externally
 *   document.querySelectorAll(".js-form-trigger").forEach((el) => {
 *     el.addEventListener("click", () => {
 *       new ModalForm(el, {
 *         fetchImpl: (url, init) => fetch(url, init),
 *         onSuccess: (result) => console.log("ok", result),
 *         onError: (message, fieldErrors) => console.warn(message, fieldErrors),
 *       });
 *     });
 *   });
 */

/**
 * Default user-facing strings. Override any subset via `options.messages`.
 *
 * @type {{
 *   form: string,
 *   submit: string,
 *   submitting: string,
 *   required: string,
 *   invalidEmail: string,
 *   validationFailed: string,
 *   requestFailed: (status: number) => string,
 *   networkError: string,
 *   close: string,
 * }}
 */
const DEFAULT_MESSAGES = {
  /** Fallback modal title when `data-title` is absent. */
  form: "Form",
  /** Fallback submit button label when `data-submit-text` is absent. */
  submit: "Submit",
  /** Submit button label while a request is in flight. */
  submitting: "Submitting…",
  /** Client-side error for a missing required field. */
  required: "This field is required",
  /** Client-side error for a malformed email address. */
  invalidEmail: "Invalid email format",
  /** Fallback message for a 422 response without a `message` field. */
  validationFailed: "Form validation failed",
  /** Fallback message for a non-OK response without a `message` field. */
  requestFailed: (status) => `Request failed: ${status}`,
  /** Fallback message for network or unexpected errors. */
  networkError: "Network error, please try again later",
  /** Accessible label for the modal close button. */
  close: "Close",
};

/**
 * @typedef {Object} ModalFormFieldOption
 * @property {string} value - The option value.
 * @property {string} label - The option label displayed to the user.
 */

/**
 * @typedef {Object} ModalFormFieldConfig
 * @property {string} name - Field name; used as the form control's `name` and for lookups.
 * @property {string} label - Human-readable label rendered above (or beside) the control.
 * @property {string} [type="text"] - One of `text`, `email`, `number`, `password`,
 *   `textarea`, `select`, `checkbox`, `file`. Defaults to `text`.
 * @property {string|number|boolean} [value=""] - Initial value. Ignored for `file` inputs.
 * @property {boolean} [required=false] - Whether the field is required.
 * @property {ModalFormFieldOption[]} [options=[]] - Options for `select` fields.
 */

/**
 * @typedef {Object} ModalFormMessages
 * @property {string} [form] - Fallback modal title.
 * @property {string} [submit] - Fallback submit button label.
 * @property {string} [submitting] - Submit button label during submission.
 * @property {string} [required] - Message for a missing required field.
 * @property {string} [invalidEmail] - Message for a malformed email.
 * @property {string} [validationFailed] - Fallback 422 message.
 * @property {(status: number) => string} [requestFailed] - Fallback non-OK message.
 * @property {string} [networkError] - Fallback network error message.
 * @property {string} [close] - Accessible label for the close button.
 */

/**
 * @typedef {Object} ModalFormOptions
 * @property {(result: any, modalForm: ModalForm) => void} [onSuccess]
 *   Invoked after a successful submit (HTTP 2xx). Receives the parsed JSON
 *   response payload and the `ModalForm` instance. The modal is closed
 *   automatically after this callback is invoked.
 * @property {(message: string, fieldErrors: Object<string,string>|undefined, modalForm: ModalForm) => void} [onError]
 *   Invoked on client-side validation failure, HTTP 422 with `errors` map,
 *   network failure, or any other error. `fieldErrors` is provided only for
 *   422 responses and maps field names to error messages.
 * @property {(url: string, init: RequestInit) => Promise<Response>} fetchImpl
 *   Required. The fetch implementation used for submission. Pass
 *   `window.fetch.bind(window)` or any compatible function. There is no
 *   built-in fallback so that production code cannot accidentally ship with
 *   a stubbed backend.
 * @property {ModalFormMessages} [messages]
 *   Partial override of `DEFAULT_MESSAGES`. Unspecified keys keep their
 *   defaults.
 */

/**
 * @typedef {Object} ModalFormTriggerDataset
 * @property {string} url - Endpoint to submit to. Required.
 * @property {string} [method="POST"] - HTTP method. Uppercased internally.
 * @property {string} [title="Form"] - Modal title.
 * @property {"sm"|"md"|"lg"} [size="md"] - Bootstrap modal size.
 * @property {string} [submitText="Submit"] - Submit button label.
 * @property {string} fields - JSON string encoding an array of `ModalFormFieldConfig`.
 */

/**
 * A reusable modal form controller.
 *
 * Reads configuration from the trigger element's `dataset`, builds the modal
 * and form DOM, handles submission, and dispatches results to caller-supplied
 * callbacks. Does not attach listeners to triggers.
 */
class ModalForm {
  /**
   * Create a `ModalForm`, build its DOM, and show it immediately.
   *
   * @param {HTMLElement} trigger
   *   The element carrying the `data-url`, `data-method`, `data-title`,
   *   `data-submit-text`, and `data-fields` attributes.
   * @param {ModalFormOptions} options
   *   Callbacks, `fetchImpl`, and optional message overrides.
   *
   * @throws {Error}
   *   Throws if `data-fields` is present but is not valid JSON, or if
   *   `fetchImpl` is not provided.
   */
  constructor(trigger, { onSuccess, onError, fetchImpl, messages } = {}) {
    if (typeof fetchImpl !== "function") {
      throw new Error(
        "ModalForm: `options.fetchImpl` is required. " +
        "Pass `window.fetch.bind(window)` or a compatible implementation."
      );
    }

    /** @type {HTMLElement} */
    this.trigger = trigger;

    /** @type {(result: any, modalForm: ModalForm) => void} */
    this.onSuccess = onSuccess || (() => {});

    /** @type {(message: string, fieldErrors: Object|undefined, modalForm: ModalForm) => void} */
    this.onError = onError || (() => {});

    /** @type {(url: string, init: RequestInit) => Promise<Response>} */
    this.fetchImpl = fetchImpl;

    /** @type {typeof DEFAULT_MESSAGES} */
    this.messages = { ...DEFAULT_MESSAGES, ...(messages || {}) };

    // --- Read configuration from dataset ---
    const {
      url,
      method = "POST",
      title = this.messages.form,
      size = "md",
      submitText = this.messages.submit,
    } = trigger.dataset;

    /** @type {string} */
    this.url = url;
    /** @type {string} */
    this.method = method.toUpperCase();
    /** @type {string} */
    this.title = title;
    /** @type {"sm"|"md"|"lg"} */
    this.size = size;
    /** @type {string} */
    this.submitText = submitText;

    /** @type {ModalFormFieldConfig[]} */
    try {
      this.fields = JSON.parse(trigger.dataset.fields || "[]");
    } catch (err) {
      throw new Error(`data-fields is not valid JSON: ${err.message}`);
    }

    // --- Internal state ---
    /** @type {string} */
    this.modalId = `modal-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    /** @type {AbortController} */
    this.abortController = new AbortController();
    /** @type {bootstrap.Modal|null} */
    this.bsModal = null;
    /** @type {HTMLElement|null} */
    this.modalEl = null;
    /** @type {HTMLFormElement|null} */
    this.form = null;
    /**
     * Map of field name to its DOM references and config.
     * @type {Map<string, {wrap: HTMLElement, input: HTMLElement, error: HTMLElement, cfg: ModalFormFieldConfig}>}
     */
    this.controls = new Map();
    /** @type {HTMLButtonElement|null} */
    this.submitBtn = null;
    /** @type {HTMLElement|null} */
    this.globalError = null;

    this._build();
  }

  /* ------------------------------------------------------------------ */
  /* Public API                                                          */
  /* ------------------------------------------------------------------ */

  /**
   * Show an error message under a specific field and mark the control invalid.
   * Passing an empty string (or any falsy value) clears the error.
   *
   * @param {string} name - Field name as declared in `data-fields`.
   * @param {string} message - Error message; empty to clear.
   * @returns {void}
   */
  setError(name, message) {
    const ctrl = this.controls.get(name);
    if (!ctrl) return;
    const { input, error } = ctrl;
    if (message) {
      error.textContent = message;
      input.classList.add("is-invalid");
      input.setAttribute("aria-invalid", "true");
      input.setAttribute("aria-describedby", error.id);
    } else {
      input.classList.remove("is-invalid");
      input.removeAttribute("aria-invalid");
      input.removeAttribute("aria-describedby");
    }
  }

  /**
   * Clear all field-level errors and hide the global error banner.
   *
   * @returns {void}
   */
  clearAllErrors() {
    for (const name of this.controls.keys()) this.setError(name, "");
    this.globalError.classList.add("d-none");
  }

  /**
   * Display a global (non-field-specific) error banner at the top of the form.
   *
   * @param {string} message
   * @returns {void}
   */
  showGlobalError(message) {
    this.globalError.textContent = message;
    this.globalError.classList.remove("d-none");
  }

  /**
   * Toggle the submit button's disabled state and label.
   *
   * @param {boolean} isSubmitting
   * @returns {void}
   */
  setSubmitting(isSubmitting) {
    this.submitBtn.disabled = isSubmitting;
    this.submitBtn.textContent = isSubmitting ? this.messages.submitting : this.submitText;
  }

  /**
   * Close the modal. Triggers the Bootstrap hide animation and aborts any
   * in-flight request. The DOM node is removed on `hidden.bs.modal`.
   *
   * @returns {void}
   */
  close() {
    this.bsModal.hide();
  }

  /**
   * Collect the current form values as a plain object. `checkbox` fields map
   * to booleans, `file` fields map to `File | null`, and all others map to
   * their string value.
   *
   * @returns {Object<string, string|boolean|File|null>}
   */
  getData() {
    return this._collect();
  }

  /* ------------------------------------------------------------------ */
  /* Private: DOM construction                                           */
  /* ------------------------------------------------------------------ */

  /**
   * Build the modal and form DOM, append them to `document.body`, and show.
   * @private
   */
  _build() {
    const { modalId, title, size } = this;

    const overlay = document.createElement("div");
    overlay.className = "modal fade";
    overlay.id = modalId;
    overlay.tabIndex = -1;
    overlay.dataset.modalId = modalId;
    overlay.setAttribute("aria-labelledby", `${modalId}-title`);
    overlay.setAttribute("aria-hidden", "true");

    const sizeClass = size === "lg" ? "modal-lg" : size === "sm" ? "modal-sm" : "";
    const dialog = document.createElement("div");
    dialog.className = `modal-dialog ${sizeClass}`.trim();

    const content = document.createElement("div");
    content.className = "modal-content";

    const header = document.createElement("div");
    header.className = "modal-header";
    const heading = document.createElement("h2");
    heading.className = "modal-title h5";
    heading.id = `${modalId}-title`;
    heading.textContent = title;
    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "btn-close";
    closeBtn.setAttribute("data-bs-dismiss", "modal");
    closeBtn.setAttribute("aria-label", this.messages.close);
    header.append(heading, closeBtn);

    const body = document.createElement("div");
    body.className = "modal-body";

    content.append(header, body);
    dialog.append(content);
    overlay.append(dialog);
    document.body.append(overlay);

    this.modalEl = overlay;

    // Form
    const form = document.createElement("form");
    form.noValidate = true;
    this.form = form;

    const globalError = document.createElement("div");
    globalError.className = "alert alert-danger d-none";
    globalError.setAttribute("role", "alert");
    form.append(globalError);
    this.globalError = globalError;

    for (const cfg of this.fields) {
      const { wrap, input, error } = this._createField(cfg);
      form.append(wrap);
      this.controls.set(cfg.name, { wrap, input, error, cfg });
    }

    const actions = document.createElement("div");
    actions.className = "text-end mt-4";
    const submitBtn = document.createElement("button");
    submitBtn.type = "submit";
    submitBtn.className = "btn btn-primary";
    submitBtn.textContent = this.submitText;
    actions.append(submitBtn);
    form.append(actions);
    this.submitBtn = submitBtn;

    body.append(form);

    const bsModal = new bootstrap.Modal(overlay, { backdrop: true, keyboard: true });
    this.bsModal = bsModal;

    overlay.addEventListener("hide.bs.modal", () => this.abortController.abort());
    overlay.addEventListener("hidden.bs.modal", () => overlay.remove(), { once: true });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      this._onSubmit();
    });

    overlay.addEventListener("shown.bs.modal", () => {
      form.querySelector("input, select, textarea")?.focus();
    }, { once: true });

    bsModal.show();
  }

  /**
   * Create a single field's wrapper, control, and error element.
   *
   * @param {ModalFormFieldConfig} cfg
   * @returns {{wrap: HTMLElement, input: HTMLElement, error: HTMLElement}}
   * @private
   */
  _createField(cfg) {
    const { name, label, type = "text", value = "", required = false, options = [] } = cfg;
    const id = `field-${name}-${Math.random().toString(36).slice(2, 7)}`;

    // Checkbox has a distinct Bootstrap structure (form-check).
    if (type === "checkbox") {
      const wrap = document.createElement("div");
      wrap.className = "form-check mb-3";
      wrap.dataset.fieldName = name;
      wrap.dataset.type = type;

      const input = document.createElement("input");
      input.type = "checkbox";
      input.className = "form-check-input";
      input.id = id;
      input.name = name;
      input.checked = Boolean(value);
      if (required) input.required = true;

      const labelEl = document.createElement("label");
      labelEl.className = "form-check-label";
      labelEl.htmlFor = id;
      labelEl.textContent = label;

      const error = document.createElement("div");
      error.className = "invalid-feedback";
      error.id = `${id}-error`;

      wrap.append(input, labelEl, error);
      return { wrap, input, error };
    }

    const wrap = document.createElement("div");
    wrap.className = "mb-3";
    wrap.dataset.fieldName = name;
    wrap.dataset.type = type;

    const labelEl = document.createElement("label");
    labelEl.className = "form-label";
    labelEl.htmlFor = id;
    labelEl.textContent = label;

    let input;
    if (type === "textarea") {
      input = document.createElement("textarea");
      input.className = "form-control";
    } else if (type === "select") {
      input = document.createElement("select");
      input.className = "form-select";
      for (const opt of options) {
        const o = document.createElement("option");
        o.value = opt.value;
        o.textContent = opt.label;
        input.append(o);
      }
    } else {
      input = document.createElement("input");
      input.type = type;
      input.className = "form-control";
    }

    input.id = id;
    input.name = name;

    if (type === "select") {
      if (value) input.value = value;
    } else if (type !== "file") {
      input.defaultValue = value;
    }
    if (required) input.required = true;

    const error = document.createElement("div");
    error.className = "invalid-feedback";
    error.id = `${id}-error`;

    wrap.append(labelEl, input, error);
    return { wrap, input, error };
  }

  /* ------------------------------------------------------------------ */
  /* Private: submission flow                                            */
  /* ------------------------------------------------------------------ */

  /**
   * Form `submit` handler: validate locally, then submit or show errors.
   * @private
   */
  _onSubmit() {
    this.clearAllErrors();
    const data = this._collect();
    const errors = this._validate(data);

    if (Object.keys(errors).length) {
      for (const [name, message] of Object.entries(errors)) {
        this.setError(name, message);
      }
      const first = Object.keys(errors)[0];
      this.controls.get(first).input.focus();
      return;
    }

    this._submitForm(data);
  }

  /**
   * Read all controls into a plain object.
   * @returns {Object<string, string|boolean|File|null>}
   * @private
   */
  _collect() {
    const fd = new FormData(this.form);
    const data = {};
    for (const [name, { input }] of this.controls) {
      if (input.type === "checkbox") data[name] = input.checked;
      else if (input.type === "file") data[name] = input.files[0] ?? null;
      else data[name] = fd.get(name);
    }
    return data;
  }

  /**
   * Perform minimal client-side validation. Only `required` and `email`
   * format are checked; server-side rules are expected to be enforced by the
   * backend (and surfaced via a 422 response).
   *
   * @param {Object} data
   * @returns {Object<string,string>} Map of field name to error message.
   * @private
   */
  _validate(data) {
    const errors = {};
    for (const [name, { input }] of this.controls) {
      if (input.required && !data[name]) {
        errors[name] = this.messages.required;
      } else if (input.type === "email" && data[name] && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data[name])) {
        errors[name] = this.messages.invalidEmail;
      }
    }
    return errors;
  }

  /**
   * Submit the collected data. Uses `FormData` when any field is a file,
   * otherwise JSON. Handles 422 responses by mapping `payload.errors` onto
   * the form fields, then invokes `onError`. All other errors are shown as a
   * global banner. Aborts are silently ignored.
   *
   * @param {Object} data
   * @returns {Promise<void>}
   * @private
   */
  async _submitForm(data) {
    this.setSubmitting(true);
    this.clearAllErrors();

    try {
      const hasFile = Object.values(data).some((v) => v instanceof File);

      let init;
      if (hasFile) {
        const fd = new FormData();
        for (const [key, val] of Object.entries(data)) {
          if (val instanceof File) {
            if (val) fd.append(key, val);
          } else {
            fd.append(key, val ?? "");
          }
        }
        init = { method: this.method, body: fd, signal: this.abortController.signal };
      } else {
        init = {
          method: this.method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
          signal: this.abortController.signal,
        };
      }

      const res = await this.fetchImpl(this.url, init);
      const payload = await res.json().catch(() => null);

      if (!res.ok) {
        if (res.status === 422 && payload?.errors) {
          for (const [name, message] of Object.entries(payload.errors)) {
            this.setError(name, message);
          }
          this.onError(payload.message || this.messages.validationFailed, payload.errors, this);
          return;
        }
        throw new Error(payload?.message || this.messages.requestFailed(res.status));
      }

      this.onSuccess(payload, this);
      this.close();
    } catch (err) {
      if (err.name === "AbortError") return;
      const message = err.message || this.messages.networkError;
      this.showGlobalError(message);
      this.onError(message, undefined, this);
    } finally {
      this.setSubmitting(false);
    }
  }
}

export default ModalForm
