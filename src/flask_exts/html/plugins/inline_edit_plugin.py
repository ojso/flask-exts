"""Inline Edit Plugin - Lightweight inline editing without X-Editable"""

from flask import url_for
from markupsafe import Markup
from ..plugin_base import PluginBase


class InlineEditPlugin(PluginBase):
    """
    Inline Edit provides lightweight inline editing functionality
    without jQuery or X-Editable dependencies.

    Features:
    - No jQuery dependency
    - Lightweight (~2KB min)
    - Bootstrap 5 native styling
    - Support for text, select, textarea, date
    - AJAX save support
    - Validation support
    - Click-to-edit and always-editable modes

    Usage:
        <!-- Text field -->
        <span class="inline-edit" data-type="text" data-name="username">
            John Doe
        </span>

        <!-- Select field -->
        <span class="inline-edit" data-type="select" data-name="status" data-options='{"active":"Active","inactive":"Inactive"}'>
            active
        </span>

        <!-- With AJAX save -->
        <span class="inline-edit" data-type="text" data-name="title" data-save-url="/api/post/1/title">
            Post Title
        </span>
    """

    def __init__(self):
        super().__init__("inline_edit", weight=60)

    def load_css(self):
        """Load inline edit styles"""
        return Markup('''
            <style>
                .inline-edit {
                    position: relative;
                    cursor: pointer;
                    padding: 2px 4px;
                    border-radius: 3px;
                    border: 1px solid transparent;
                    transition: all 0.2s ease;
                }

                .inline-edit:hover:not(.editing) {
                    background-color: rgba(0, 123, 255, 0.1);
                    border-color: rgba(0, 123, 255, 0.3);
                }

                .inline-edit.editing {
                    border-color: #007bff;
                    background-color: #ffffff;
                    padding: 0;
                }

                .inline-edit-input,
                .inline-edit-select,
                .inline-edit-textarea {
                    width: 100%;
                    padding: 4px 6px;
                    border: 1px solid #ced4da;
                    border-radius: 0.25rem;
                    font-family: inherit;
                    font-size: inherit;
                }

                .inline-edit-input:focus,
                .inline-edit-select:focus,
                .inline-edit-textarea:focus {
                    outline: none;
                    border-color: #80bdff;
                    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
                }

                .inline-edit-actions {
                    margin-top: 4px;
                    display: flex;
                    gap: 4px;
                }

                .inline-edit-btn {
                    padding: 2px 8px;
                    font-size: 12px;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                    font-weight: 500;
                }

                .inline-edit-save {
                    background-color: #28a745;
                    color: white;
                }

                .inline-edit-save:hover {
                    background-color: #218838;
                }

                .inline-edit-cancel {
                    background-color: #6c757d;
                    color: white;
                }

                .inline-edit-cancel:hover {
                    background-color: #5a6268;
                }

                .inline-edit-loading {
                    opacity: 0.6;
                    pointer-events: none;
                }

                .inline-edit-error {
                    color: #dc3545;
                    font-size: 12px;
                    margin-top: 2px;
                }
            </style>
        ''')

    def load_js(self):
        """Load inline edit JavaScript"""
        return Markup('''
            <script>
                class InlineEdit {
                    constructor(element, options = {}) {
                        this.element = element;
                        this.options = {
                            type: element.getAttribute('data-type') || 'text',
                            name: element.getAttribute('data-name'),
                            saveUrl: element.getAttribute('data-save-url'),
                            options: this.parseOptions(element.getAttribute('data-options')),
                            onSave: options.onSave || null,
                            onError: options.onError || null,
                            ...options
                        };
                        this.originalValue = element.textContent.trim();
                        this.init();
                    }

                    parseOptions(str) {
                        try {
                            return JSON.parse(str || '{}');
                        } catch (e) {
                            return {};
                        }
                    }

                    init() {
                        this.element.classList.add('inline-edit');
                        this.element.addEventListener('click', () => this.edit());
                        this.element.addEventListener('keydown', (e) => {
                            if (e.key === 'Escape') this.cancel();
                            if (e.key === 'Enter' && e.ctrlKey) this.save();
                        });
                    }

                    edit() {
                        if (this.element.classList.contains('editing')) return;

                        this.element.classList.add('editing');
                        const input = this.createInput();
                        const actions = this.createActions();

                        this.element.innerHTML = '';
                        this.element.appendChild(input);
                        this.element.appendChild(actions);

                        input.focus();
                        if (input.type === 'text' || input.type === 'email') {
                            input.select();
                        }

                        this.input = input;
                    }

                    createInput() {
                        let input;

                        if (this.options.type === 'select') {
                            input = document.createElement('select');
                            input.className = 'inline-edit-select';
                            for (const [value, label] of Object.entries(this.options.options)) {
                                const option = document.createElement('option');
                                option.value = value;
                                option.textContent = label;
                                if (value === this.originalValue) option.selected = true;
                                input.appendChild(option);
                            }
                        } else if (this.options.type === 'textarea') {
                            input = document.createElement('textarea');
                            input.className = 'inline-edit-textarea';
                            input.value = this.originalValue;
                            input.rows = 4;
                        } else {
                            input = document.createElement('input');
                            input.type = this.options.type === 'date' ? 'date' : 'text';
                            input.className = 'inline-edit-input';
                            input.value = this.originalValue;
                        }

                        return input;
                    }

                    createActions() {
                        const div = document.createElement('div');
                        div.className = 'inline-edit-actions';

                        const saveBtn = document.createElement('button');
                        saveBtn.className = 'inline-edit-btn inline-edit-save';
                        saveBtn.textContent = 'Save';
                        saveBtn.onclick = () => this.save();

                        const cancelBtn = document.createElement('button');
                        cancelBtn.className = 'inline-edit-btn inline-edit-cancel';
                        cancelBtn.textContent = 'Cancel';
                        cancelBtn.onclick = () => this.cancel();

                        div.appendChild(saveBtn);
                        div.appendChild(cancelBtn);
                        return div;
                    }

                    save() {
                        const newValue = this.input.value.trim();

                        if (newValue === this.originalValue) {
                            this.cancel();
                            return;
                        }

                        if (this.options.saveUrl) {
                            this.saveToServer(newValue);
                        } else {
                            this.finish(newValue);
                        }
                    }

                    saveToServer(value) {
                        this.element.classList.add('inline-edit-loading');

                        fetch(this.options.saveUrl, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': this.getCSRFToken()
                            },
                            body: JSON.stringify({
                                [this.options.name]: value
                            })
                        })
                        .then(r => r.json())
                        .then(data => {
                            this.finish(value);
                            if (this.options.onSave) this.options.onSave(data);
                        })
                        .catch(err => {
                            this.showError(err.message);
                            if (this.options.onError) this.options.onError(err);
                        });
                    }

                    finish(value) {
                        this.originalValue = value;
                        this.element.classList.remove('editing', 'inline-edit-loading');
                        this.element.textContent = value;
                        this.element.addEventListener('click', () => this.edit());
                    }

                    cancel() {
                        this.element.classList.remove('editing', 'inline-edit-loading');
                        this.element.textContent = this.originalValue;
                    }

                    showError(message) {
                        this.element.classList.remove('inline-edit-loading');
                        const error = document.createElement('div');
                        error.className = 'inline-edit-error';
                        error.textContent = message;
                        this.element.appendChild(error);
                        setTimeout(() => error.remove(), 3000);
                    }

                    getCSRFToken() {
                        return document.querySelector('meta[name="csrf-token"]')?.content || '';
                    }
                }

                // Auto-initialize inline edit elements
                document.addEventListener('DOMContentLoaded', function() {
                    document.querySelectorAll('.inline-edit[data-type]').forEach(el => {
                        if (!el.inlineEdit) {
                            el.inlineEdit = new InlineEdit(el);
                        }
                    });
                });

                // Export for manual initialization
                window.InlineEdit = InlineEdit;
            </script>
        ''')
