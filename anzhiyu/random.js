var posts=["2024/07/10/GPT-4提示工程大赛冠军/","2024/07/10/hello-world/","2024/07/11/三种常见的网格细化技术/"];function toRandomPost(){
    pjax.loadUrl('/'+posts[Math.floor(Math.random() * posts.length)]);
  };