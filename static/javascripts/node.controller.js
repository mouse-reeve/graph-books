function NodeController ($location, $routeParams, $scope, Graph) {
    var nodeId = $routeParams.id || null;
    var label = $routeParams.label || '';

    $scope.searchName;
    var builderBlank = {
        startId: nodeId,
        relationship: '',
        endId: null
    }

    $scope.builder = angular.copy(builderBlank);

    if (!!nodeId) {
        Graph.getNode(nodeId).then(function (node) {
            if (label !== node.label) {
                $location.path('/'+node.label+'/'+nodeId);
            }
            $scope.node = node;
        });
    }

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
                $scope.builder.relationship,
                $scope.builder.endId).then(function (node) {
            $scope.node = node;
            $scope.searchName = '';
            $scope.searchResults = null;
            $scope.builder = angular.copy(builderBlank);
        });
    };
}
