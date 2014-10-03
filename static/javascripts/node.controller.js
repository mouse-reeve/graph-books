function NodeController ($scope, Graph, $routeParams) {
    var nodeId = $routeParams.id || 0;

    Graph.getNode(nodeId).then(function (node) {
        console.log(node);
        $scope.node = node;
    });
}
