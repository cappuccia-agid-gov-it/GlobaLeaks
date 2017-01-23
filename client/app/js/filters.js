angular.module('GLFilters', []).
filter('weekNumber', function() {
  return function (value) {
    var date = new Date(value);
    date.setHours(0, 0, 0, 0);
    // Thursday in current week decides the year.
    date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
    // January 4 is always in week 1.
    var week1 = new Date(date.getFullYear(), 0, 4);
    // Adjust to Thursday in week 1 and count number of weeks from date to week1.
    return 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000 - 3 + (week1.getDay() + 6) % 7) / 7);
  };
}).
filter('newExpirationDate', function() {
  return function(tip) {
    return new Date(new Date().getTime() + tip.timetolive * 24 * 3600 * 1000);
  };
}).
filter('anomalyToString', function() {
  return function (anomaly) {
    var anomalies = {
      'started_submissions': 'Started submissions',
      'completed_submissions': 'Completed submissions',
      'failed_submissions': 'Failed submissions',
      'failed_logins': 'Failed logins',
      'successful_logins': 'Successful logins',
      'files': 'Files',
      'comments': 'Comments',
      'messages': 'Messages'
    };

    return anomalies[anomaly];
  };
}).
filter('tipFileName', ['$filter', function($filter) {
  return function(tip) {
    if (angular.isDefined(tip)) {
      var d = $filter('date')(tip.creation_date, 'yyyyMMdd', '0');
      return d + '-' + tip.progressive;
    }
  };
}]).
filter('wbfileCreator', [function() {
  return function(rec_id, rec_list) {
    for (var i = 0; i < rec_list.length; i++) {
      if (rec_id === rec_list[i].id) {
        return rec_list[i]['name'];
      }
    }
    // TODO log fact that receiver_id was not found
    return 'Unknown';
  };
}]).
filter('wbAccessRevoked', ['$filter', function($filter) {
  return function(wb_last_access, wbtip_timetolive) {
    if (angular.isUndefined(wb_last_access)) {
      return undefined;
    }
    var a = new Date(wb_last_access);
    var revokeDate = new Date(a.setDate(wbtip_timetolive));

    return $filter('date')(revokeDate, 'dd-MM-yyyy HH:mm');
  };
}]);
