angular.module('app', [
        'graphFactory',
        'ngRoute'])

.config(function ($routeProvider, $locationProvider) {
    $routeProvider
        .when('/', {
            controller: 'NodeController',
            templateUrl: 'static/partials/start.html'
        })
        .when('/:label/:id', {
            controller: 'NodeController',
            templateUrl: 'static/partials/node.html'
        })
        .otherwise({
            redirectTo: '/'
        });

    $locationProvider.html5Mode(true);
})

.run(function () {
    //I dunno maybe I'll need the root scope for something
});


