var p1;
var p2;
var p3;
var p4;
var days;

$(document).ready(function(){
function myfun(){
   jQuery.ajax({
       method: "GET",
       url: "/tickets",
     success: function( tickets ) {
          //console.log(tickets.tickets);
          var p1_tickets=tickets['tickets'][0];
          var p2_tickets=tickets['tickets'][1];
          var p3_tickets=tickets['tickets'][2];
          var p4_tickets=tickets['tickets'][3];
          //days = tickets['ticket_count']['Days'];
          p1 = tickets['tickets'][0].length;
          p2 = tickets['tickets'][1].length;
          p3 = tickets['tickets'][2].length;
          p4 = tickets['tickets'][3].length;
          change_reqs = tickets['change'];
          //console.log(p1_tickets);
          //console.log(p2_tickets);
          var color='';
          var ins = '';
          var c=''
          for(var i in change_reqs){
            console.log(change_reqs[i]['start']);
            var st = change_reqs[i]['start'];
            var stp = change_reqs[i]['stop'];
            var ticket = change_reqs[i]['ticket_id'];
            c += '<tr><th scope="row">'+i+'</th><td>Pfizer</td><td>'+ticket+'</td><td>'+st+'  '+stp+'</td></tr>';
           } jQuery('#changes').html(c);
	
          for(var i in p1_tickets) {
              if(p1_tickets[i]['Time Left']=='Breached'){
                  color = 'badge-danger';
              }else if(p1_tickets[i]['Time Left'].split("h")[0]<1 || p1_tickets[i]['Time Left'].split("h")[0].includes("m")){
                  color = 'badge-danger';
              }else if(p1_tickets[i]['Time Left'].split("h")[0]<2){
                  color = 'badge-warning';
              }else if(p1_tickets[i]['Time Left'].split("h")[0]<3){
                  color = 'badge-primary';
              }else if(p1_tickets[i]['Time Left'].split("h")[0]<4){
                  color = 'badge-success';
              };
              if(p1_tickets[i]['Time Left']!=='Breached') {
                  ins += "<li class=\"list-group-item\">\n" + "<a href=\"#\"> <i class=\"fa fa-envelope-o\"></i>" + p1_tickets[i]['ticket_id'] + "<span style='margin-left: 40px'>"+p1_tickets[i]['org']+"</span><span class=\"timer-pause  badge " + color + " pull-right\">" + p1_tickets[i]['Time Left'] +"</span></a>\n" + "</li>";
              }
              else {
                  ins += "<li class=\"list-group-item\">\n" + "<a href=\"#\"> <i class=\"fa fa-envelope-o\"></i>" + p1_tickets[i]['ticket_id'] + "<span style='margin-left: 40px'>"+p1_tickets[i]['org']+"</span><span class=\"badge " + color + " pull-right\"  id=" + i + ">"+ p1_tickets[i]['Time Left'] +"</span></a>\n" + "</li>";
              }

          }jQuery('#p1').html(ins);
          var ins = '';
          for(var i in p2_tickets) {
              console.log(p2_tickets[i]["Time Left"].split("h")[0]);
              if(p2_tickets[i]['Time Left']=='Breached'){
                  color = 'badge-danger';
              }else if(p2_tickets[i]['Time Left'].split("h")[0]<1 || p2_tickets[i]['Time Left'].split("h")[0].includes("m")){
                  color = 'badge-danger';
              }else if(p2_tickets[i]['Time Left'].split("h")[0]<2){
                  color = 'badge-warning';
              }else if(p2_tickets[i]['Time Left'].split("h")[0]<3){
                  color = 'badge-primary';
              }else if(p2_tickets[i]['Time Left'].split("h")[0]<4){
                  color = 'badge-success';
              };
              if(p2_tickets[i]['Time Left']!=='Breached') {
                  ins += "<li class=\"list-group-item\">\n" + "<a href=\"#\"> <i class=\"fa fa-envelope-o\"></i>" + p2_tickets[i]['ticket_id'] + "<span style='margin-left: 40px'>"+p2_tickets[i]['org']+"</span><span class=\"timer-pause  badge " + color + " pull-right\">" + p2_tickets[i]['Time Left'] +"</span></a>\n" + "</li>";
              }
              else {
                  ins += "<li class=\"list-group-item\">\n" + "<a href=\"#\"> <i class=\"fa fa-envelope-o\"></i>" + p2_tickets[i]['ticket_id'] + "<span style='margin-left: 40px'>"+p2_tickets[i]['org']+"</span><span class=\"badge " + color + " pull-right\"  id=" + i + ">"+ p2_tickets[i]['Time Left'] +"</span></a>\n" + "</li>";
              }


          }jQuery('#p2').html(ins);
          var ins = '';
          for(var i in p3_tickets) {
              if(p3_tickets[i]['Time Left']=='Breached'){
                  color = 'badge-danger';
              }else if(p3_tickets[i]['Time Left'].split("h")[0]<2 || p3_tickets[i]['Time Left'].split("h")[0].includes("m")){
                  color = 'badge-danger';
              }else if(p3_tickets[i]['Time Left'].split("h")[0]<4){
                  color = 'badge-warning';
              }else if(p3_tickets[i]['Time Left'].split("h")[0]<6){
                  color = 'badge-primary';
              }else if(p3_tickets[i]['Time Left'].split("h")[0]<8){
                  color = 'badge-success';
              };
              var Minutes = p3_tickets[i]['Time Left'];
              if(p3_tickets[i]['Time Left']!=='Breached') {
                  ins += "<li class=\"list-group-item\">\n" + "<a href=\"#\"> <i class=\"fa fa-envelope-o\"></i>" + p3_tickets[i]['ticket_id'] + "<span style='margin-left: 40px'>"+p3_tickets[i]['org']+"</span><span class=\"timer-pause  badge " + color + " pull-right\">" + p3_tickets[i]['Time Left'] +"</span></a>\n" + "</li>";
              }
              else {
                  ins += "<li class=\"list-group-item\">\n" + "<a href=\"#\"> <i class=\"fa fa-envelope-o\"></i>" + p3_tickets[i]['ticket_id'] + "<span style='margin-left: 40px'>"+p3_tickets[i]['org']+"</span><span class=\"badge " + color + " pull-right\"  id=" + i + ">"+ p3_tickets[i]['Time Left'] +"</span></a>\n" + "</li>";
              }

          }jQuery('#p3').html(ins);
          var ins = '';
          for(var i in p4_tickets) {
              console.log(i);
              if(p4_tickets[i]['Time Left']=='Breached'){
                  color = 'badge-danger';
              }else if(p4_tickets[i]['Time Left'].split("h")[0]<2 || p4_tickets[i]['Time Left'].split("h")[0].includes("m")){
                  color = 'badge-danger';
              }else if(p4_tickets[i]['Time Left'].split("h")[0]<4){
                  color = 'badge-warning';
              }else if(p4_tickets[i]['Time Left'].split("h")[0]<6){
                  color = 'badge-primary';
              }else if(p4_tickets[i]['Time Left'].split("h")[0]<8){
                  color = 'badge-success';
              };
              if(p4_tickets[i]['Time Left']!=='Breached') {
                  ins += "<li class=\"list-group-item\">\n" + "<a href=\"#\"> <i class=\"fa fa-envelope-o\"></i>" + p4_tickets[i]['ticket_id'] + "<span style='margin-left: 40px'>"+p4_tickets[i]['org']+"</span><span class=\"timer-pause  badge " + color + " pull-right\">" + p4_tickets[i]['Time Left'] +"</span></a>\n" + "</li>";
              }
              else {
                  ins += "<li class=\"list-group-item\">\n" + "<a href=\"#\"> <i class=\"fa fa-envelope-o\"></i>" + p4_tickets[i]['ticket_id'] + "<span style='margin-left: 40px'>"+p4_tickets[i]['org']+"</span><span class=\"badge " + color + " pull-right\"  id=" + i + ">"+ p4_tickets[i]['Time Left'] +"</span></a>\n" + "</li>";
              }
          }jQuery('#p4').html(ins);
          jQuery('#p1count').text(p1);
          jQuery('#p2count').text(p2);
          jQuery('#p3count').text(p3);
          jQuery('#p4count').text(p4);
          if(tickets.new_p1.length > 0){
              var x = document.getElementById("high");
              x.play();
          };
            }
     });

};
setInterval(myfun, 2000);
});
