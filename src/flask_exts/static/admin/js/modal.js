$('#fa_modal_window').on('show.bs.modal', function (event) {
    let relatedTarget = $(event.relatedTarget)
    let modal = $(this)
    modal.find('.modal-content').load(relatedTarget.attr('href'))
})
