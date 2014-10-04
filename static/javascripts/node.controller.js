function NodeController ($scope, Graph, $routeParams) {
    var nodeId = $routeParams.id || 0;
    var label = $routeParams.label || '';

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

    $scope.pickPronoun = function () {
        return $scope.node.label === 'person' ? 'their' : 'its';
    };
}
