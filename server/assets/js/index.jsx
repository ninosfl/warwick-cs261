/* jshint esversion: 6 */

import React from 'react';
import ReactDOM from 'react-dom';
import Button from '@material-ui/core/Button';
import { DataList } from './list-reports';

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
if (target = document.querySelector('#report-list')) {
  ReactDOM.render(<DataList />, target);
}
