// Call the dataTables jQuery plugin
$(document).ready(function() {
  const table = $('#dataTable').DataTable({
    drawCallback: function() {
      const api = this.api();

      api.rows({ page: 'current' }).every(function(rowIdx, tableLoop, rowLoop) {
        const serialNumber = rowLoop + 1;
        $(this.node()).find('td:first').text(serialNumber);
      });
    }
  });

  table.draw();
});
