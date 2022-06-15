const app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        blockchain: [],
        openTransactions: [],
        wallet: null,
        view: 'chain',
        walletLoading: false,
        txLoading: false,
        dataLoading: false,
        showElement: null,
        error: null,
        success: null,
        funds: 0,
        outgoingTx: {
            recipient: '',
            amount: 0,
        },
    },
    computed: {
        loadedData: function () {
            if (this.view === 'chain') {
                return this.blockchain;
            } else {
                return this.openTransactions;
            }
        },
    },
    methods: {
        onCreateWallet: function () {
            // Send Http request to create a new wallet (and return keys)
            const vm = this;
            vm.walletLoading = true;
            axios
                .get('/wallet')
                .then(function (response) {
                    vm.error = null;
                    vm.success = `Wallet ready.<br>Public Key: ${response.data.response.public_key.slice(
                        0,
                        10
                    )}...${response.data.response.public_key.slice(
                        response.data.response.public_key.length - 10
                    )}<br>Private Key: ${response.data.response.private_key.slice(
                        0,
                        10
                    )}...${response.data.response.private_key.slice(
                        response.data.response.private_key.length - 10
                    )}`;
                    vm.wallet = {
                        public_key: response.data.response.public_key,
                        private_key: response.data.response.private_key,
                    };
                    vm.funds = response.data.response.balance;
                    vm.walletLoading = false;
                })
                .catch(function (error) {
                    vm.success = null;
                    vm.error = error.response.data.response.message;
                    vm.wallet = null;
                    vm.walletLoading = false;
                });
        },
        onLoadWallet: function () {
            // Send Http request to load an existing wallet (from a file on the server)
            vm = this;
            vm.onCreateWallet();
        },
        onSendTx: function () {
            // Send Transaction to backend
            const vm = this;
            vm.txLoading = true;
            axios
                .post('/transaction', {
                    recipient: vm.outgoingTx.recipient,
                    amount: vm.outgoingTx.amount,
                })
                .then(function (response) {
                    vm.error = null;
                    vm.success = response.data.response.message;
                    vm.funds = response.data.response.balance;
                    vm.txLoading = false;
                })
                .catch(function (error) {
                    vm.success = null;
                    vm.error = error.response.data.response.message;
                    vm.txLoading = false;
                });
        },
        onMine: function () {
            const vm = this;
            axios
                .post('/mine')
                .then(function (response) {
                    vm.error = null;
                    vm.success = response.data.response.message;
                    vm.funds = response.data.response.balance;
                })
                .catch(function (error) {
                    vm.success = null;
                    vm.error = error.response.data.response.message;
                });
        },
        onLoadData: function () {
            const vm = this;
            vm.dataLoading = true;
            if (this.view === 'chain') {
                // Load blockchain data
                axios
                    .get('/blockchain')
                    .then(function (response) {
                        vm.blockchain = response.data.blockchain;
                        vm.dataLoading = false;
                    })
                    .catch(function (error) {
                        vm.dataLoading = false;
                        vm.error = 'Something went wrong.';
                    });
            } else {
                // Load transaction data
                axios
                    .get('/transactions')
                    .then(function (response) {
                        vm.openTransactions = response.data.transactions;
                        vm.dataLoading = false;
                    })
                    .catch(function (error) {
                        vm.dataLoading = false;
                        vm.error = 'Something went wrong.';
                    });
            }
        },
    },
});
