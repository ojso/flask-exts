class ModelAction {
    constructor(actionErrorMessage, actionConfirmations) {
        this.actionErrorMessage = actionErrorMessage;
        this.actionConfirmations = actionConfirmations;
        this.init();
    }

    init = () => {
        this.rowToggle = document.querySelector('.action-rowtoggle');
        this.inputs = document.querySelectorAll('input.action-checkbox');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Master toggle functionality: when master checkbox changes
        this.rowToggle.addEventListener('change', (event) => {
            // Set all individual checkboxes to match master checkbox state
            this.inputs.forEach(input => {
                input.checked = event.target.checked;
            });
        });

        // Individual checkbox functionality: when any individual checkbox changes
        this.inputs.forEach(input => {
            input.addEventListener('change', () => {
                // Check if all individual checkboxes are checked
                const allInputsChecked = Array.from(this.inputs).every(input => input.checked);
                // Update master checkbox to reflect the overall state
                this.rowToggle.checked = allInputsChecked;
            });
        });
    }

    execute(name) {
        if (document.querySelectorAll('input.action-checkbox:checked').length === 0) {
            alert(this.actionErrorMessage);
            return false;
        }

        const msg = this.actionConfirmations[name];
        if (msg) {
            if (!confirm(msg)) {
                return false;
            }
        }

        // Update hidden form and submit it
        const form = document.getElementById('action_form');

        // Remove existing action checkboxes from form
        const formCheckboxes = form.querySelectorAll('input.action-checkbox');
        formCheckboxes.forEach(checkbox => {
            checkbox.remove();
        });

        // Add cloned copies of checked checkboxes to form
        const checkedCheckboxes = document.querySelectorAll('input.action-checkbox:checked');
        checkedCheckboxes.forEach(checkbox => {
            form.appendChild(checkbox.cloneNode(true));
        });

        // Set action value and submit form
        form.querySelector('input[name="action"]').value = name;
        form.submit();
        return false;
    };
}



