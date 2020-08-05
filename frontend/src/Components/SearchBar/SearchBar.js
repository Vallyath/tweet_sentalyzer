import React from 'react';

class SearchBar extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            topic: ""
        }
    }

    handleTextChange = (event) => {
        this.setState({topic: event.target.value})
    }

    search = () => {
        const requestBody = {
            headers: {"Content-Type": "application/json"},
            method: "POST",
            body: JSON.stringify({topic: this.state.topic})
        }
        return fetch('http://localhost:5000/topic', requestBody).then(res => res.json())
    }

    submitSearch = () => {
        this.search();
    }

    render(){
        return (
            <div className="form-row">
                <div className="col-5 offset-3">
                    <input className="form-control" placeholder="Enter a topic" onChange={this.handleTextChange}/>
                </div>
                <div className="col-3">
                    <button className="btn btn-light" onClick={this.submitSearch}>Search</button>
                </div>
            </div>
        )
    }
}

export default SearchBar;
