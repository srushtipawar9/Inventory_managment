// Call the dataTables jQuery plugin
$(document).ready(function() {
  const table = $('#dataTable').DataTable({
    // Initial configuration
  });

  // Function to regenerate serial numbers based on search and sort
  // Only applies if the first column header is 'SR', '#' or 'No.'
  table.on('order.dt search.dt draw.dt', function () {
    const firstHeader = table.column(0).header().textContent.trim();
    if (['SR', '#', 'No.'].includes(firstHeader)) {
      table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
        cell.innerHTML = i + 1;
      });
    }
  }).draw();
});
