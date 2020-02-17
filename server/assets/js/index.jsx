/* jshint esversion: 6 */

import React from 'react';
import ReactDOM from 'react-dom';
import Button from '@material-ui/core/Button';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';

function App() {
  return (
    <Button variant="contained" color="primary">
      Hello World
    </Button>
  );
}

// Define list item link component
function ListItemLink(props) {
  return <ListItem button component="a" {...props} />;
}

// Define DataList component
function DataList(props) {
  // Get list of data!
  let data = JSON.parse(document.getElementById('list-data').textContent);

  let listItems = data.map((number) =>
    <div>
      <ListItemLink href={number.toString() + "/"} key={number.toString()}>
        <ListItemText primary={number.toString()} />
      </ListItemLink>
      <Divider />
    </div>)

  return <List>{listItems}</List>;
}

// Try different render targets, rendering to the one that appears first
let target = null;
if (target = document.querySelector('#react-app')) {
  ReactDOM.render(<App />, target);
} else if (target = document.querySelector('#report-list')) {
  ReactDOM.render(<DataList />, target);
}
