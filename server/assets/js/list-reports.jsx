/* jshint esversion: 6 */

import React from 'react';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';

const monthNames = {
    "1": "January",
    "2": "February",
    "3": "March",
    "4": "April",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "August",
    "9": "September",
    "10": "October",
    "11": "November",
    "12": "December"
};

// Define list item link component
function ListItemLink(props) {
    return <ListItem button component="a" {...props} />;
}

function ListLink(props) {
    return (<>
        <ListItemLink href={props.id + "/"}>
            <ListItemText primary={props.text} />
        </ListItemLink>
        {props.index < props.limit && <Divider />}
    </>);
}
  
// Define Year component
function YearList(props) {
    // Get list of data!
    let data = JSON.parse(document.getElementById('list-data').textContent);
    let limit = data.length - 1;

    // Function to avoid computing toString multiple times
    let func = (k, i) =>
        <ListLink key={k} id={k} text={k} index={i} limit={limit} />;
    
    // Transform each element in the list to the corresponding link element
    let listItems = data.map((n, i) => func(n.toString(), i));

    return <List>{listItems}</List>;
}

function MonthList(props) {
    // Get list of data!
    let data = JSON.parse(document.getElementById('list-data').textContent);
    let year = JSON.parse(document.getElementById('year').textContent);
    let limit = data.length - 1;

    // Create the ListLink component from the inputs
    let func = (k, i) =>
        <ListLink key={k} id={k} index={i} text={monthNames[k] + year} limit={limit} />;
    
    // Transform each element in the list to the corresponding link element
    let listItems = data.map((n, i) => func(n.toString(), i));

    return <List>{listItems}</List>;
}

export { DataList, MonthList };