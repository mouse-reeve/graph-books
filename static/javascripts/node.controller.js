function NodeController ($scope, Graph, $routeParams) {
    var nodeId = $routeParams.id || 0;

    Graph.getNode(nodeId).then(function (node) {
        $scope.node = node;
    });

    $scope.pickPronoun = function () {
        return $scope.node.labels[0] === 'person' ? 'their' : 'it\'s';
    };
}
