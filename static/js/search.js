/**
 * Search & Filter — Client-side real-time search, department filter, and table sorting.
 */

(function () {
    'use strict';

    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-department');
    const tbody = document.getElementById('students-tbody');
    const noResults = document.getElementById('no-results');
    const studentCount = document.getElementById('student-count');
    const tableWrapper = document.querySelector('.table-wrapper');

    if (!searchInput || !tbody) return;

    // ── Search + Filter ──

    function filterTable() {
        const query = searchInput.value.toLowerCase().trim();
        const dept = filterSelect ? filterSelect.value : '';

        const rows = tbody.querySelectorAll('tr');
        let visibleCount = 0;

        rows.forEach((row) => {
            const name = row.dataset.name || '';
            const roll = row.dataset.roll || '';
            const rowDept = row.dataset.department || '';

            const matchesSearch = !query || name.includes(query) || roll.includes(query);
            const matchesDept = !dept || rowDept === dept;

            if (matchesSearch && matchesDept) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Update count
        if (studentCount) {
            studentCount.textContent = visibleCount;
        }

        // Show/hide no-results message
        if (noResults && tableWrapper) {
            if (visibleCount === 0) {
                noResults.style.display = '';
                tableWrapper.style.display = 'none';
            } else {
                noResults.style.display = 'none';
                tableWrapper.style.display = '';
            }
        }
    }

    // Debounced search
    searchInput.addEventListener('input', window.debounce(filterTable, 300));

    if (filterSelect) {
        filterSelect.addEventListener('change', filterTable);
    }


    // ── Column Sorting ──

    let currentSort = { column: null, ascending: true };

    document.querySelectorAll('#students-table th[data-sort]').forEach((th) => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;

            // Toggle direction
            if (currentSort.column === column) {
                currentSort.ascending = !currentSort.ascending;
            } else {
                currentSort.column = column;
                currentSort.ascending = true;
            }

            // Remove sorted class from all headers
            document.querySelectorAll('#students-table th').forEach((h) => h.classList.remove('sorted'));
            th.classList.add('sorted');

            // Sort rows
            const rows = Array.from(tbody.querySelectorAll('tr'));
            rows.sort((a, b) => {
                const aVal = getCellValue(a, column);
                const bVal = getCellValue(b, column);

                let comparison = 0;
                if (column === 'marks') {
                    comparison = parseFloat(aVal) - parseFloat(bVal);
                } else {
                    comparison = aVal.localeCompare(bVal, undefined, { numeric: true });
                }

                return currentSort.ascending ? comparison : -comparison;
            });

            // Re-append sorted rows
            rows.forEach((row) => tbody.appendChild(row));

            // Update sort icon
            const icon = th.querySelector('.sort-icon');
            if (icon) {
                icon.textContent = currentSort.ascending ? '↑' : '↓';
            }
        });
    });

    function getCellValue(row, column) {
        const mapping = {
            roll_number: 0,
            name: 1,
            department: 2,
            marks: 3,
        };
        const idx = mapping[column];
        if (idx === undefined) return '';
        const td = row.children[idx];
        return td ? td.textContent.trim().toLowerCase() : '';
    }

})();
