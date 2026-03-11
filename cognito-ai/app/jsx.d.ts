declare global {
  namespace JSX {
    interface IntrinsicElements {
      div: any;
      main: any;
      h1: any;
      h2: any;
      h3: any;
      h4: any;
      h5: any;
      h6: any;
      p: any;
      span: any;
      a: any;
      button: any;
      input: any;
      form: any;
      html: any;
      head: any;
      body: any;
      title: any;
      meta: any;
      link: any;
      script: any;
      style: any;
      [elemName: string]: any;
    }
  }
}

export {};
