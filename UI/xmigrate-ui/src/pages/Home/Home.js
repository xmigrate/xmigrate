import React, { Component } from 'react'
import HeaderComponent from '../../components/HeaderComponent/HeaderComponent'
import SideNavbar from '../../components/SideNavbar/SideNavbar'

import { Switch, Route } from "react-router-dom";
import BluePrint from '../BluePrint/BluePrint';
import Discover from '../Discover/Discover';
export default class Home extends Component {
    render() {
        return (
            <div className="Home h-100 d-flex flex-column">
                <HeaderComponent />
                <div className="container-fluid media-body ">
                    <div className="row h-100">
                        <SideNavbar />
                        
                        <Route path="/blue-print" exact strict component={BluePrint} />
                        <Route path="/discover" exact strict component={Discover} />

                    </div>
                </div>

                <Switch>

                </Switch>

            </div>
        )
    }
}
