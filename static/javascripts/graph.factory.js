angular.module('graphFactory', []).factory('Graph', function ($http) {
    return {
        getNode: function (nodeId) {
            return $http.get('/api/node/' + nodeId).then(function (response) {
                return response.data;
            });
        }
    };
});
