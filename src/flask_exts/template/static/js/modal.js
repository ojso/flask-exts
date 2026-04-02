document.addEventListener('DOMContentLoaded', function (cb = null) {
    const modalElement = document.getElementById('fa_modal_window');
    if (!modalElement) {
        console.warn('Modal element with id "fa_modal_window" not found.');
        return;
    }

    // Listen for the Bootstrap 'show.bs.modal' event
    // modalElement.addEventListener('show.bs.modal', function (event) {
    $('#fa_modal_window').on('show.bs.modal', function (event) {
        // 1. Get the element that triggered the modal (the button/link clicked)
        const relatedTarget = event.relatedTarget;

        // 2. Extract the URL from the 'href' attribute of the trigger or from a data attribute
        const url = relatedTarget.dataset.href || relatedTarget.getAttribute('href');
        if (!url) {
            console.warn('No href found on the trigger element.');
            return;
        }

        // 3. this refers to the modal element itself
        const modal = this;

        // 4. Find the container inside the modal where content will be loaded
        const contentContainer = modal.querySelector('.modal-content');

        // 5. Fetch the content from the URL
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                // Insert the fetched HTML into the container
                contentContainer.innerHTML = html;

                // 6. Execute the callback function
                if (typeof cb === 'function') {
                    cb();
                }
            })
            .catch(error => {
                console.error('Error loading modal content:', error);
                contentContainer.innerHTML = '<div class="alert alert-danger">Failed to load content.</div>';
            });
    });

});