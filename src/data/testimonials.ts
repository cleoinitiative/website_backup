export interface Testimonial {
  quote: string;
  author: string;
  role: string;
  video?: string;
  image?: string;
}

export const testimonials: Testimonial[] = [
  {
    quote: "A huge amount of fulfillment comes from being able to make such a positive impact on the lives of others.",
    author: "Chase Alley",
    role: "Senior from Canterbury School",
    video: "/videos/testimonial1.mp4",
    image: "/testimonials/chase.jpg"
  },
  {
    quote: "Teaching seniors technology has been one of the most rewarding experiences of my high school career.",
    author: "Sarah Johnson",
    role: "Junior at Riverdale High",
    video: "/videos/testimonial2.mp4",
    image: "/testimonials/sarah.jpg"
  },
  {
    quote: "The connections we make with seniors go far beyond just teaching technology.",
    author: "Michael Chen",
    role: "Chapter Leader at Oak Ridge",
    video: "/videos/testimonial3.mp4",
    image: "/testimonials/michael.jpg"
  }
]; 