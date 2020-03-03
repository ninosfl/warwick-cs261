/* jshint esversion: 9 */

import React, { useContext } from 'react';
import { Typography } from '@material-ui/core';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import PublishIcon from '@material-ui/icons/Publish';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { actionTypes, FormDispatch, useStyles } from './form-constants';

export { FormFieldWrapper, SubmitField, SubmitButton, NextButton, SubFormTitle };


// Component for text fields in the form
function FormField(props) {
    // Get dispatch function from the reducer hook via a context hook
    // TODO: Move this out if this proves expensive
    const dispatch = useContext(FormDispatch);

    // Fetch defined styling
    const classes = useStyles(props);

    // Create a function that takes in an event, and dispatches the appropriate
    // action to the reducer hook.
    const handleChange = e => dispatch({
        input: props.id,
        type: actionTypes.new,
        newValue: e.target.value
    });

    return (
        <TextField
            variant="outlined"
            onChange={handleChange}
            className={classes.formItem}
            {...props}
        />
    );
}


// Component for text fields that need correction in the form
function ErrorFormField(props) {
    // Set the anchor element on the menu
    const [anchor, setAnchor] = React.useState(null);

    // Functions for setting the menu anchor to the current form field
    const whenFocused = event => setAnchor(event.currentTarget);
    // TODO: When leaving, dispatch with type actionTypes.correction ??
    const whenLeaving = () => setAnchor(null);

    // Make suggestions React elements
    const suggestions = props.suggestions.map((s, i) =>
        <MenuItem onClick={whenLeaving} key={i}>{s}</MenuItem>
    );

    return (
    <>
        <FormField error helperText="Click here to see correction values" aria-controls="simple-menu" aria-haspopup="true" onClick={whenFocused} {...props}/>
        <Menu
            id="simple-menu"
            anchorEl={anchor}
            keepMounted
            open={Boolean(anchor)}
            onClose={whenLeaving}
        >
            <MenuItem disabled={true}>Please select a correction:</MenuItem>
            {suggestions}
            <MenuItem onClick={whenLeaving}>Stick with: {props.value}</MenuItem>
        </Menu>
    </>);
}


function FormFieldWrapper(props) {
    // Display field normally if no suggestions available
    if (props.suggestions.length === 0) {
        return (
            <FormField
                id={props.id}
                label={props.label}
                value={props.value}
                onBlur={props.onBlur}
            />);

    } else { // Otherwise, return an error field
        return (
            <ErrorFormField
                id={props.id}
                label={props.label}
                value={props.value}
                onBlur={props.onBlur}
                suggestions={props.suggestions}
            />);
    }
}


function SubmitField(props) {
    // Get dispatch function from the reducer hook via a context hook
    // TODO: Move this out if this proves expensive
    const dispatch = useContext(FormDispatch);

    // Fetch defined styling
    const classes = useStyles(props);

    // Create a function that takes in an event, and dispatches the appropriate
    // action to the reducer hook.
    const handleChange = e => dispatch({
        input: props.id,
        type: actionTypes.new,
        newValue: e.target.value
    });

    return (
        <TextField
            variant="standard"
            size="small"
            onChange={handleChange}
            className={classes.formItem}
            {...props}
        />
    );
}


function NextButton(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Fetch dispatch function from context
    const dispatch = useContext(FormDispatch);

    // Event function to get the SuperForm to render the next SubForm
    const goToNextForm = () => dispatch({ type: actionTypes.nextForm });

    return (
        <Button
            variant="contained"
            color="primary"
            className={classes.button}
            endIcon={<NavigateNextIcon />}
            onClick={goToNextForm}
            {...props}
        >
            Next Page
        </Button>
    );
}


function SubmitButton(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    return (
        <Button
            variant="contained"
            color="primary"
            className={classes.button}
            endIcon={<CloudUploadIcon />}
            // endIcon={<PublishIcon />}
            {...props}
        >
            Submit
        </Button>
    );
}


function SubFormTitle(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    return (
        <Typography variant="h4" gutterBottom className={classes.formTitle} {...props}/>
    );
}