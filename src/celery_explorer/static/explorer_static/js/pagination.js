function goToPage() {
    var pageInput = document.getElementById('page-input');
    var pageNum = parseInt(pageInput.value);
    var maxPages = parseInt(pageInput.max);
    
    if (pageNum >= 1 && pageNum <= maxPages) {
        window.location.href = '?page=' + pageNum;
    } else {
        alert('Pleas, input page number from 1 to ' + maxPages);
    }
}