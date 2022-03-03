import './ErrorPage.scss';
import { FaUndo } from 'react-icons/fa'


export default function ErrorPage(props) {
    console.log(props);
    if (props.err === "500") {
        return (
            <div className="error">
                <div className="container">
                    <div className="segment">
                        <div className="glitch">
                            <span className="symbol shallow">500</span>
                            <span className="symbol deep">500</span>
                            <span className="line"></span>
                        </div>
                    </div>
                    <div className="txtError">!! Internal Server Error</div>

                    <div className="Ico"><FaUndo size={30} onClick={() => { window.location.replace("/") }} /></div>
                </div>
            </div>
        )
    } else if (props.err === "404") {
        return (
            <div className="error">
                <div className="container">
                    <div className="segment">
                        <div className="glitch">
                            <span className="symbol shallow">404</span>
                            <span className="symbol deep">404</span>
                            <span className="line"></span>
                        </div>
                    </div>
                    <div className="txtError">!!!Server not Found</div>
                    <div className="Ico"><FaUndo size={30} onClick={() => { window.location.replace("/") }} /></div>
                </div>
            </div>
        )
    } else if (props.err === "401") {
        return (
            <div className="error">
                <div className="container">
                    <div className="segment">
                        <div className="glitch">
                            <span className="symbol shallow">401</span>
                            <span className="symbol deep">401</span>
                            <span className="line"></span>
                        </div>
                    </div>
                    <div className="txtError">!!!Unauthorized Access</div>
                    <div className="Ico"><FaUndo size={30} onClick={() => { window.location.replace("/") }} /></div>
                </div>
            </div>
        )
    } else if (props.err === "400") {
        return (
            <div className="error">
                <div className="container">
                    <div className="segment">
                        <div className="glitch">
                            <span className="symbol shallow">400</span>
                            <span className="symbol deep">400</span>
                            <span className="line"></span>
                        </div>
                    </div>
                    <div className="txtError">!!!Request Error</div>
                    <div className="Ico"><FaUndo size={30} onClick={() => { window.location.replace("/") }} /></div>
                </div>
            </div>
        )
    }

}