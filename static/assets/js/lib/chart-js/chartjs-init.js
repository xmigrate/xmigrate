( function ( $ ) {
    "use strict";


    //doughut chart
    var ctx = document.getElementById( "pfizerChart" );
    ctx.height = 250;
    var myChart = new Chart( ctx, {
        type: 'doughnut',
        data: {
            datasets: [ {
                data: [ 45, 25, 20],
                backgroundColor: [
                                    "green",
                                    "red",
                                    "rgba(0, 123, 255,0.5)"
                                ],
                hoverBackgroundColor: [
                                    "rgba(0, 123, 255,0.9)",
                                    "rgba(0, 123, 255,0.7)",
                                    "rgba(0, 123, 255,0.5)"
                                ]

                            } ],
            labels: [
                            "Running",
                            "Stopped",
                            "Terminated"
                        ]
        },
        options: {
            responsive: true
        }
    } );

    var ctx = document.getElementById( "agiChart" );
    ctx.height = 250;
    var myChart = new Chart( ctx, {
        type: 'doughnut',
        data: {
            datasets: [ {
                data: [ 45, 25, 20],
                backgroundColor: [
                                    "green",
                                    "red",
                                    "rgba(0, 123, 255,0.5)"
                                ],
                hoverBackgroundColor: [
                                    "rgba(0, 123, 255,0.9)",
                                    "rgba(0, 123, 255,0.7)",
                                    "rgba(0, 123, 255,0.5)"
                                ]

                            } ],
            labels: [
                            "Running",
                            "Stopped",
                            "Terminated"
                        ]
        },
        options: {
            responsive: true
        }
    } );




} )( jQuery );