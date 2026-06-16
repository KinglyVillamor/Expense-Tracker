// ============================================
// ExpenseTracker - Main Application Logic
// ============================================

// Global Variables
let categoryChart = null;
let trendChart = null;
let currentTransactions = [];
let currentFilter = 'all';
let isBackendConnected = false;

// ============================================
// Auto-Categorization Engine
// ============================================

function autoCategorize(description) {
    const desc = description.toLowerCase();
    const rules = {
        'Income': ['salary', 'paycheck', 'deposit', 'payment received', 'refund', 'income', 'bonus'],
        'Food & Dining': ['starbucks', 'mcdonalds', 'kfc', 'pizza', 'restaurant', 'cafe', 'food', 'lunch', 'dinner', 'burger', 'groceries', 'grocery'],
        'Transport': ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'shell', 'metro', 'bus', 'train', 'parking', 'toll'],
        'Shopping': ['amazon', 'walmart', 'target', 'best buy', 'costco', 'ebay', 'shop', 'store', 'mall', 'nike', 'zara'],
        'Bills & Utilities': ['electric', 'water', 'internet', 'netflix', 'spotify', 'phone', 'utility', 'bill', 'cable', 'subscription'],
        'Entertainment': ['cinema', 'movie', 'theater', 'concert', 'game', 'steam', 'playstation', 'xbox'],
        'Healthcare': ['pharmacy', 'doctor', 'hospital', 'clinic', 'medical', 'prescription', 'dentist'],
        'Travel': ['flight', 'hotel', 'airbnb', 'booking', 'vacation', 'trip', 'airline']
    };
    
    for (const [category, keywords] of Object.entries(rules)) {
        if (keywords.some(keyword => desc.includes(keyword))) {
            return category;
        }
    }
    return 'Other';
}

// ============================================
// Connection Status
// ============================================

function updateConnectionStatus(connected) {
    isBackendConnected = connected;
    const statusDiv = document.getElementById('connectionStatus');
    if (connected) {
        statusDiv.className = 'connection-status status-online';
        statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Connected to Database';
        setTimeout(() => {
            if (statusDiv) statusDiv.style.opacity = '0.5';
        }, 3000);
    } else {
        statusDiv.className = 'connection-status status-offline';
        statusDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Offline Mode (Demo Data)';
    }
}

// ============================================
// Data Loading
// ============================================

async function loadTransactions() {
    try {
        const response = await fetch('http://localhost:8000/transactions');
        if (!response.ok) throw new Error('Server error');
        const data = await response.json();
        currentTransactions = data.transactions || [];
        updateConnectionStatus(true);
        updateUI();
    } catch (error) {
        console.error('Backend not available:', error);
        updateConnectionStatus(false);
        if (currentTransactions.length === 0) loadDemoData();
        else updateUI();
    }
}

function loadDemoData() {
    currentTransactions = [
        { id: 1, amount: 5200, description: "Monthly Salary", category: "Income", date: new Date().toISOString().split('T')[0], auto_tagged: false },
        { id: 2, amount: 125.50, description: "Starbucks Coffee", category: "Food & Dining", date: new Date().toISOString().split('T')[0], auto_tagged: true },
        { id: 3, amount: 45.00, description: "Uber Ride", category: "Transport", date: new Date().toISOString().split('T')[0], auto_tagged: true },
        { id: 4, amount: 89.99, description: "Amazon Shopping", category: "Shopping", date: new Date().toISOString().split('T')[0], auto_tagged: true },
        { id: 5, amount: 180.00, description: "Electric Bill", category: "Bills & Utilities", date: new Date().toISOString().split('T')[0], auto_tagged: true },
        { id: 6, amount: 15.99, description: "Netflix Subscription", category: "Entertainment", date: new Date().toISOString().split('T')[0], auto_tagged: true },
        { id: 7, amount: 65.00, description: "Pharmacy", category: "Healthcare", date: new Date().toISOString().split('T')[0], auto_tagged: true }
    ];
    updateUI();
}

// ============================================
// UI Updates
// ============================================

function updateUI() {
    updateStats();
    renderChart();
    renderTrendChart();
    renderTransactionsTable();
}

function updateStats() {
    const income = currentTransactions.filter(t => t.category === 'Income').reduce((s, t) => s + t.amount, 0);
    const expenses = currentTransactions.filter(t => t.category !== 'Income').reduce((s, t) => s + t.amount, 0);
    const balance = income - expenses;
    const savingsRate = income > 0 ? ((balance / income) * 100).toFixed(1) : 0;
    
    document.getElementById('totalBalance').innerHTML = `$${balance.toFixed(2)}`;
    document.getElementById('totalIncome').innerHTML = `$${income.toFixed(2)}`;
    document.getElementById('totalExpenses').innerHTML = `$${expenses.toFixed(2)}`;
    document.getElementById('savingsRate').innerHTML = `${savingsRate}%`;
}

// ============================================
// Charts
// ============================================

function renderChart() {
    const categoryMap = new Map();
    currentTransactions.forEach(tx => {
        if (tx.category !== 'Income') {
            categoryMap.set(tx.category, (categoryMap.get(tx.category) || 0) + tx.amount);
        }
    });
    
    const ctx = document.getElementById('categoryChart').getContext('2d');
    if (categoryChart) {
        categoryChart.data.labels = Array.from(categoryMap.keys());
        categoryChart.data.datasets[0].data = Array.from(categoryMap.values());
        categoryChart.update();
    } else {
        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: { 
                labels: Array.from(categoryMap.keys()), 
                datasets: [{ 
                    data: Array.from(categoryMap.values()), 
                    backgroundColor: ['#3b82f6', '#f97316', '#10b981', '#ef4444', '#8b5cf6', '#f59e0b', '#06b6d4', '#ec489a'], 
                    borderWidth: 0 
                }] 
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: true, 
                plugins: { legend: { position: 'right' } } 
            }
        });
    }
}

function renderTrendChart() {
    const monthly = new Map();
    currentTransactions.forEach(tx => {
        const month = new Date(tx.date || new Date()).toLocaleString('default', { month: 'short' });
        if (!monthly.has(month)) monthly.set(month, { income: 0, expenses: 0 });
        const data = monthly.get(month);
        tx.category === 'Income' ? data.income += tx.amount : data.expenses += tx.amount;
    });
    
    const ctx = document.getElementById('trendChart').getContext('2d');
    if (trendChart) {
        trendChart.data.labels = Array.from(monthly.keys());
        trendChart.data.datasets[0].data = Array.from(monthly.values()).map(v => v.income);
        trendChart.data.datasets[1].data = Array.from(monthly.values()).map(v => v.expenses);
        trendChart.update();
    } else {
        trendChart = new Chart(ctx, {
            type: 'line', 
            data: { 
                labels: Array.from(monthly.keys()), 
                datasets: [
                    { 
                        label: 'Income', 
                        data: Array.from(monthly.values()).map(v => v.income), 
                        borderColor: '#10b981', 
                        backgroundColor: 'rgba(16, 185, 129, 0.1)', 
                        tension: 0.4, 
                        fill: true 
                    },
                    { 
                        label: 'Expenses', 
                        data: Array.from(monthly.values()).map(v => v.expenses), 
                        borderColor: '#ef4444', 
                        backgroundColor: 'rgba(239, 68, 68, 0.1)', 
                        tension: 0.4, 
                        fill: true 
                    }
                ] 
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }
}

// ============================================
// Transactions Table
// ============================================

function renderTransactionsTable() {
    const tbody = document.getElementById('transactionsList');
    let filtered = currentFilter === 'all' ? currentTransactions : 
                  (currentFilter === 'Income' ? currentTransactions.filter(t => t.category === 'Income') : 
                  currentTransactions.filter(t => t.category !== 'Income'));
    
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    if (searchTerm) {
        filtered = filtered.filter(t => 
            t.description.toLowerCase().includes(searchTerm) || 
            t.category.toLowerCase().includes(searchTerm)
        );
    }
    
    if (!filtered.length) { 
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:3rem;">No transactions found</td></tr>'; 
        return; 
    }
    
    tbody.innerHTML = filtered.map(tx => `
        <tr class="transaction-row">
            <td><strong>${escapeHtml(tx.description)}</strong></td>
            <td>${tx.date || new Date().toISOString().split('T')[0]}</td>
            <td>
                <select class="category-select-table" data-id="${tx.id}" style="width:130px;">
                    ${['Food & Dining','Transport','Shopping','Bills & Utilities','Entertainment','Income','Healthcare','Travel','Other'].map(cat => 
                        `<option value="${cat}" ${tx.category === cat ? 'selected' : ''}>${cat}</option>`
                    ).join('')}
                </select>
            </td>
            <td class="${tx.category === 'Income' ? 'amount-positive' : 'amount-negative'}">
                ${tx.category === 'Income' ? '+' : '-'}$${Math.abs(tx.amount).toFixed(2)}
            </td>
            <td>
                <button class="delete-btn-table" onclick="deleteTransaction(${tx.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
    
    document.querySelectorAll('.category-select-table').forEach(select => { 
        select.addEventListener('change', (e) => updateCategory(parseInt(select.dataset.id), select.value)); 
    });
}

function escapeHtml(str) { 
    return str.replace(/[&<>]/g, function(m) { 
        if (m === '&') return '&amp;'; 
        if (m === '<') return '&lt;'; 
        if (m === '>') return '&gt;'; 
        return m; 
    }); 
}

// ============================================
// Export Report
// ============================================

function exportReport() {
    const dataStr = JSON.stringify(currentTransactions, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `expense_report_${new Date().toISOString().split('T')[0]}.json`;
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

// ============================================
// API Calls
// ============================================

async function addTransaction(amount, description, category) { 
    const formData = new FormData(); 
    formData.append('amount', amount); 
    formData.append('description', description); 
    formData.append('category', category === 'auto' ? autoCategorize(description) : category); 
    
    try { 
        const response = await fetch('http://localhost:8000/transactions', { method: 'POST', body: formData }); 
        if (response.ok) await loadTransactions(); 
    } catch (error) { 
        const newTx = { 
            id: Date.now(), 
            amount: parseFloat(amount), 
            description, 
            category: category === 'auto' ? autoCategorize(description) : category, 
            date: new Date().toISOString().split('T')[0], 
            auto_tagged: true 
        }; 
        currentTransactions.push(newTx); 
        updateUI(); 
    } 
}

async function updateCategory(id, category) { 
    if (isBackendConnected) {
        try { 
            const formData = new FormData(); 
            formData.append('category', category); 
            await fetch(`http://localhost:8000/update-category/${id}`, { method: 'POST', body: formData }); 
            await loadTransactions(); 
        } catch (error) { 
            const tx = currentTransactions.find(t => t.id === id); 
            if (tx) tx.category = category; 
            updateUI(); 
        } 
    } else {
        const tx = currentTransactions.find(t => t.id === id); 
        if (tx) tx.category = category; 
        updateUI(); 
    }
}

async function deleteTransaction(id) { 
    if (!confirm('Delete this transaction?')) return; 
    
    if (isBackendConnected) {
        try { 
            await fetch(`http://localhost:8000/transactions/${id}`, { method: 'DELETE' }); 
            await loadTransactions(); 
        } catch (error) { 
            const index = currentTransactions.findIndex(t => t.id === id); 
            if (index !== -1) currentTransactions.splice(index, 1); 
            updateUI(); 
        } 
    } else {
        const index = currentTransactions.findIndex(t => t.id === id); 
        if (index !== -1) currentTransactions.splice(index, 1); 
        updateUI(); 
    }
}

async function uploadCSV(file) { 
    if (!file) return; 
    const formData = new FormData(); 
    formData.append('file', file); 
    
    try { 
        await fetch('http://localhost:8000/upload-csv', { method: 'POST', body: formData }); 
        await loadTransactions(); 
        alert('CSV imported successfully!'); 
    } catch (error) { 
        alert('CSV upload failed - Backend not running'); 
    } 
}

// ============================================
// Modal Functions
// ============================================

function openAddModal() { 
    document.getElementById('addModal').classList.add('active'); 
}

function closeAddModal() { 
    document.getElementById('addModal').classList.remove('active'); 
}

// ============================================
// Event Listeners
// ============================================

// Form submission
document.getElementById('txForm').addEventListener('submit', async (e) => { 
    e.preventDefault(); 
    await addTransaction(
        document.getElementById('amount').value, 
        document.getElementById('description').value, 
        document.getElementById('categorySelect').value
    ); 
    document.getElementById('amount').value = ''; 
    document.getElementById('description').value = ''; 
    closeAddModal(); 
});

// Search input
document.getElementById('searchInput').addEventListener('input', () => renderTransactionsTable());

// Filter chips
document.querySelectorAll('.filter-chip').forEach(chip => { 
    chip.addEventListener('click', () => { 
        document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active')); 
        chip.classList.add('active'); 
        currentFilter = chip.dataset.filter; 
        renderTransactionsTable(); 
    }); 
});

// Close modal when clicking outside
window.onclick = (event) => { 
    const modal = document.getElementById('addModal'); 
    if (event.target === modal) closeAddModal(); 
};

// ============================================
// Initialize Application
// ============================================

loadTransactions();