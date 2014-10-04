angular.module('graphFactory', []).factory('Graph', function ($http) {
    return {
        getNode: function (nodeId) {
            return $http.get('/api/node/' + nodeId).then(function (response) {
                return response.data;
            });
        },

        lookup: function (name) {
            return $http.get('/api/name-lookup/' + name).then(function (response) {
                return response.data;
            });
        },

        linkNodes: function (startId, relationship, endId) {
            var data = {start: startId,
                        relationship: relationship,
                        end: endId}
            return $http.post('/api/node/relationships', data).then(function (response) {
                return response.data;
            });
        }
    };
});
