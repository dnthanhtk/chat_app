import axios from 'axios'
import React from 'react'



class Message extends React.Component
{

    state ={
        chat: [],
        msg: ''
    }
    

    handleChange = (e) =>{
        console.log(e.target.value)
        this.setState({msg:e.target.value})
    }
    handleSend = ()=>{
        if (this.state.msg !=='')
        {
            axios.post('http://172.23.0.4:9999/getreponse',{'msg':this.state.msg})
            .then(res=>{
                console.log(res.data)
                let ch = this.state.chat;
                ch.push({from:'our',msag:this.state.msg});
                ch.push({from:'cb',msag:res.data.intent});
                if (res.data.entity.length>0)
                {
                    for (let i=0;i<res.data.entity.length;i++)
                    {
                        ch.push({from:'cb',msag:res.data.entity[i]})
                    }
                }


                this.setState({chat:ch,msg:''});
                console.log(this.state);
                
            })
            .catch(err=>{
                console.log(err);
            });
            let interval = window.setInterval(function(){
                    var elem = document.getElementById('chatt');
                    elem.scrollTop = elem.scrollHeight;
                    window.clearInterval(interval);
                },1000);
            this.forceUpdate();

            
        
        }
    }
    render()
    {
        return (
            <div>
                <div id='chatt' style={{overflow:'scroll',overflowX:'hidden',height:'85vh'}}>
                {
                    this.state.chat.map((msg)=>{
                        if(msg.from === 'cb')
                        {
                            return <div style={{flexWrap:'wrap',fontSize:'25px',
                            marginBottom:'10px',borderRadius:'100px',marginRight:'500px',
                            padding:'10px',paddingBottom:'20px',width:'30%',
                            backgroundColor:'black',color:'white',float:'left',
                            display:'block'}}>{msg.msag} </div>
                        }
                        else{
                        return <div style={{flexWrap:'wrap',fontSize:'25px',
                        marginBottom:'10px',borderRadius:'100px',marginLeft:'500px',
                        padding:'10px',paddingBottom:'20px',width:'30%',backgroundColor:'orange',
                        float:'right',display:'block',color:'whitesmoke'}}>{msg.msag}</div>
                        }
                    })
                }
                </div>
                <div style={{height:'1vh'}}>
                    <input type='text' name='msg'
                        onChange={(e)=>this.handleChange(e)} 
                        class="form-control"
                        placeholder='Nhập text'
                        style={{width:'90%',float:'left'}}
                        value={this.state.msg}/>
                        <button onClick={()=>this.handleSend()} style={{paddingLeft:'25px',paddingRight:'25px'}} class ="btn btn-primary">Send</button>

                </div>
            
                
                {/* <form style={{display: 'flex'}} onSubmit={()=>this.handleSend()}>
                    <input
                        
                        onChange={(e)=>this.handleChange(e)} 

                        placeholder='Nhập text'
                        style={{width:'90%',float:'left'}}
                        value={this.state.msg}
                    />
                    <input type='submit' value='Get predict' className='btn' />
                </form> */}
            </div>
        )
    }
}
export default Message;