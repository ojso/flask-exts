$('body').on('click.modal.data-api', '[data-toggle="modal"]', function () {
    $($(this).data("target") + ' .modal-content').load($(this).attr('href'));
});
