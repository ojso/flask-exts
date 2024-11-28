class AdminModelActions {
    constructor(actionErrorMessage, actionConfirmations) {
        this.actionErrorMessage = actionErrorMessage;
        this.actionConfirmations = actionConfirmations;

        $(function () {
            $('.action-rowtoggle').change(function () {
                $('input.action-checkbox').prop('checked', this.checked);
            });
        });

        $(function () {
            const inputs = $('input.action-checkbox');
            inputs.change(function () {
                let allInputsChecked = true;
                for (let i = 0; i < inputs.length; i++) {
                    if (!inputs[i].checked) {
                        allInputsChecked = false;
                        break;
                    }
                }
                $('.action-rowtoggle').attr('checked', allInputsChecked);
            });
        });
    }

    execute(name) {
        const selected = $('input.action-checkbox:checked').length;

        if (selected === 0) {
            alert(this.actionErrorMessage);
            return false;
        }

        const msg = this.actionConfirmations[name];

        if (!!msg)
            if (!confirm(msg))
                return false;

        // Update hidden form and submit it
        const form = $('#action_form');
        $('#action', form).val(name);

        $('input.action-checkbox', form).remove();
        $('input.action-checkbox:checked').each(function () {
            form.append($(this).clone());
        });

        form.submit();
        return false;
    };
}

let modelActions = new AdminModelActions(JSON.parse($('#message-data').text()), JSON.parse($('#actions-confirmation-data').text()));
