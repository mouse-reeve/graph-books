angular.module('app', [
        'graphFactory',
        'ngRoute'])

.config(function ($routeProvider) {
    $routeProvider
        .when('/', {
            controller: 'NodeController',
            templateUrl: 'static/partials/start.html'
        })
        .when('/:id', {
            controller: 'NodeController',
            templateUrl: 'static/partials/start.html'
        })
        .otherwise({
            redirectTo: '/'
        });
})

.run(function () {
    //I dunno maybe I'll need the root scope for something
});


