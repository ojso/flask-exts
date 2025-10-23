const timeoutChange = 2000;


// Changes element textContent for two seconds, then changes it back
function temporarilyBtnChangeSuccess(btn) {
    oldText = btn.textContent;
    btn.textContent = '\u2713';
    btn.classList.add('btn-success')
    setTimeout(() => { 
        btn.textContent = oldText; 
        btn.classList.remove('btn-success')
    }, timeoutChange);
}

function copyToClipboard(text, cb = () => { }) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(cb);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            cb();
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
        }
        document.body.removeChild(textArea);
    }
}

function downloadTextToFile(text, filename = 'download.txt') {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}