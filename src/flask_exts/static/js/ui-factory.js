/**
 * Utility functions for creating form fields and modals.
 */

function createEl({ tag = "div", className = "", attributes = {}, textContent = "" } = {}) {
    const el = document.createElement(tag);
    if (className) {
        el.className = className;
    }
    if (textContent !== undefined && textContent !== null) {
        el.textContent = String(textContent);
    }
    const booleanAttrs = ['disabled', 'readonly', 'required', 'checked', 'multiple', 'selected'];
    Object.entries(attributes).forEach(([key, value]) => {
        if (value == null) return;
        if (booleanAttrs.includes(key)) {
            if (value) {
                el.setAttribute(key, '');
            } else {
                el.removeAttribute(key);
            }
        } else {
            el.setAttribute(key, String(value));
        }
    });
    return el;
}

function createInputField({ type, className = "", attrs = {} } = {}) {
    return createEl({ tag: 'input', className, attributes: { type, ...attrs } });
}

function createTextareaField({ className = "", attrs = {} } = {}) {
    return createEl({ tag: 'textarea', className, attributes: attrs });
}

function createSelectField({ className = "", attrs = {}, options = [] } = {}) {
    const selectEl = createEl({ tag: 'select', className, attributes: attrs });
    options.forEach(option => {
        let optionEl;
        if (typeof option === 'string') {
            optionEl = createEl({ tag: 'option', attributes: { value: option }, textContent: option });
        } else if (typeof option === 'object' && option !== null) {
            const { label, value, ...rest } = option;
            optionEl = createEl({ tag: 'option', className: '', attributes: { value, ...rest }, textContent: label });
        }
        if (optionEl) {
            selectEl.appendChild(optionEl);
        }
    });
    return selectEl;
}

function createSwitchField({ className = "", attrs = {} } = {}) {
    const field = createEl({ tag: 'div', className });
    field.classList.add("form-switch");
    const checkbox = createEl({ tag: 'input', className: "form-check-input", attributes: { type: 'checkbox', ...attrs } });
    field.appendChild(checkbox);
    return field;
}

function createModal({
    title = "✎",
    cancelText = "✗",
    saveText = "✓",
    backdrop = true,
    keyboard = true,
    focus = true
} = {}) {
    const overlay = createEl({ tag: 'div', className: 'modal fade', attributes: { tabindex: -1 } });

    const modalDialog = createEl({ tag: 'div', className: 'modal-dialog' });
    overlay.appendChild(modalDialog);

    const modalContent = createEl({ tag: 'div', className: 'modal-content' });
    modalDialog.appendChild(modalContent);

    const modalHeader = createEl({ tag: 'div', className: 'modal-header' });
    modalContent.appendChild(modalHeader);

    const titleEl = createEl({ tag: 'h5', className: 'modal-title', textContent: title });
    modalHeader.appendChild(titleEl);

    const closeButton = createEl({
        tag: 'button',
        className: 'btn-close',
        attributes: { type: 'button', 'data-bs-dismiss': 'modal', 'aria-label': 'Close' }
    });
    modalHeader.appendChild(closeButton);

    const body = createEl({ tag: 'div', className: 'modal-body' });
    modalContent.appendChild(body);

    const errorEl = createEl({ tag: 'div', className: 'alert alert-danger d-none' });
    body.appendChild(errorEl);

    const footer = createEl({ tag: 'div', className: 'modal-footer' });
    modalContent.appendChild(footer);

    const cancelButton = createEl({
        tag: 'button',
        className: 'btn btn-secondary',
        attributes: { type: 'button', 'data-bs-dismiss': 'modal', 'aria-label': 'Close' },
        textContent: cancelText
    });
    footer.appendChild(cancelButton);

    const saveButton = createEl({ tag: 'button', className: 'btn btn-primary', attributes: { type: 'button' }, textContent: saveText });
    footer.appendChild(saveButton);

    const modal = new bootstrap.Modal(overlay, { backdrop, keyboard, focus });
    return { modal, overlay, titleEl, body, errorEl, cancelButton, saveButton };
}

 function showToast(message, type = 'success', delay = 5000) {
    const colors = {
      success: 'bg-success',
      danger: 'bg-danger',
      warning: 'bg-warning',
      info: 'bg-info'
    };
    const bg = colors[type] || 'bg-primary';

    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'position-fixed top-0 end-0 p-3';
      container.style.zIndex = 1050;
      document.body.appendChild(container);    }

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white ${bg} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast, { delay });
    bsToast.show();

    // toast.addEventListener('hidden.bs.toast', function () {
    //   toast.remove();
    //   if (container.children.length === 0) container.remove();
    // });
  }

export {
    createInputField,
    createTextareaField,
    createSelectField,
    createSwitchField,
    createModal,
    showToast,
}
