/* jshint esversion: 6 */

import React from 'react';
import ReactDOM from 'react-dom';
import Button from '@material-ui/core/Button';
import { YearList, MonthList } from './list-reports';

function App() {
  return (
    <Button variant="contained" color="primary">
      Hello World
    </Button>
  );
}

// Try different render targets, rendering to the one that appears first
let target = null;
if (target = document.querySelector('#react-app')) {
  ReactDOM.render(<App />, target);
}
if (target = document.querySelector('#report-list-years')) {
  ReactDOM.render(<YearList />, target);
}
if (target = document.querySelector('#report-list-months')) {
  ReactDOM.render(<MonthList />, target);
}
