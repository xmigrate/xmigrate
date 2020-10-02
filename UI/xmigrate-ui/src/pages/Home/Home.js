import React, { Component } from 'react'
import HeaderComponent from '../../components/HeaderComponent/HeaderComponent'
import SideNavbar from '../../components/SideNavbar/SideNavbar';
import BluePrint from '../BluePrint/BluePrint';
import Discover from '../Discover/Discover';
import {ProtectedRoute} from '../../services/Protected.route';
export default class Home extends Component {
    render() {
        return (
            <div className="Home h-100 d-flex flex-column">
                <HeaderComponent />
                <div className="container-fluid media-body ">
                    <div className="row h-100">
                        <SideNavbar />
                        <ProtectedRoute exact strict path="/home/blue-print" component={BluePrint} />
                        <ProtectedRoute exact strict path="/home/discover" component={Discover} />
                    </div>
                </div>

          

               

            </div>
        )
    }
}
