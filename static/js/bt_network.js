const app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        nodes: [],
        newNodeUrl: '',
        error: null,
        success: null,
    },
    methods: {
        onAddNode: function () {
            // Add node as peer node to local node server
            vm = this;
            axios
                .post('/node', { node: vm.newNodeUrl })
                .then(function (response) {
                    vm.success = 'Stored node successfully.';
                    vm.error = null;
                    vm.nodes = response.data.response.nodes;
                })
                .catch(function (error) {
                    vm.success = null;
                    vm.error = error.response.data.response.message;
                });
        },
        onLoadNodes: function () {
            // Load all peer nodes of the local node server
            vm = this;
            axios
                .get('/nodes')
                .then(function (response) {
                    vm.success = 'Fetched nodes successfully.';
                    vm.error = null;
                    vm.nodes = response.data.response.nodes;
                })
                .catch(function (error) {
                    vm.success = null;
                    vm.error = error.response.data.response.message;
                });
        },
        onRemoveNode: function (nodeURL) {
            // Remove node as a peer node
            vm = this;
            axios
                .delete(`/node/${nodeURL}`)
                .then(function (response) {
                    vm.success = 'Node removed successfully.';
                    vm.error = null;
                    vm.nodes = response.data.response.nodes;
                })
                .catch(function (error) {
                    vm.success = null;
                    vm.error = error.response.data.response.message;
                });
        },
    },
});
