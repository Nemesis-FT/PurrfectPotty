import {AppContext} from "./Context";
import {useState} from "react";
import Routing from "./Routing";
import {Bluelib} from "@steffo/bluelib-react";
import {LayoutThreeCol} from "@steffo/bluelib-react";
import Style from "./App.css"

function App() {
    const [token, setToken] = useState(null);
    const [address, setAddress] = useState(null)
    return (
        <Bluelib theme={"amber"} backgroundColor={"#161616"} accentColor={"#346751"} foregroundColor={"#ECDBBA"}>
            <LayoutThreeCol>
                <LayoutThreeCol.Center>
                    <div className="App">
                        <AppContext.Provider value={{token, setToken, address, setAddress}}>
                            <Routing/>
                        </AppContext.Provider>
                    </div>
                </LayoutThreeCol.Center>
            </LayoutThreeCol>
        </Bluelib>
    );
}

export default App;
