$('#fa_modal_window').on('show.bs.modal', function (event) {
    let relatedTarget = $(event.relatedTarget)
    let modal = $(this)
    modal.find('.modal-content').load(relatedTarget.attr('href'), function () {
        // window.faForm.applyGlobalStyles(document.getElementsByClassName('modal-content'));
        // window.faForm.applyGlobalStyles(modal.find('.modal-content'), true);
    })
})
