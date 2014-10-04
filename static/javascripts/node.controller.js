function NodeController ($scope, Graph, $routeParams) {
    var nodeId = $routeParams.id || 0;
    var label = $routeParams.label || '';

    $scope.searchName;
    $scope.builder = {
        startId: nodeId,
        relationship: '',
        endId: null
    }

    Graph.getNode(nodeId).then(function (node) {
        $scope.node = node;
    });

    $scope.getTemplate = function () {
        var knownLabels = ['book', 'person', 'year'];
        if (knownLabels.indexOf(label) !== -1) {
            return 'static/partials/' + label +'.html';
        } else {
            return 'static/partials/generic.html';
        }
    };

    $scope.lookup = function () {
        Graph.lookup($scope.searchName).then(function (results) {
            $scope.searchResults = results;
        });
    };

    $scope.linkNodes = function () {
        Graph.linkNodes($scope.builder.startId,
                $scope.builder.relationship, $scope.builder.endId);
    };
}
